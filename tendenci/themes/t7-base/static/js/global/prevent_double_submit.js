/*
 * Ignore a second submit on the same form until the next page load, and
 * show a spinner while that request is in progress.
 *
 * A form can opt out with data-allow-repeat-submit.
 *
 * Scripts that cancel the submit event and later call form.submit()
 * themselves (reCAPTCHA v3) mark the form with data-tendenci-async-submit
 * during the submit event. The lock and spinner stay up until that
 * navigation. If the async submit fails, dispatch tendenci:submit-cancelled
 * on the form so the buttons can be used again.
 *
 * A cancelled submit without that attribute (a confirmation dialog, or a
 * payment form that stays on the page) releases the lock immediately.
 */
(function () {
    var LOCK = 'data-submitting';
    var ASYNC = 'data-tendenci-async-submit';
    var OWNED = 'data-tendenci-owned-submit';
    var MARK = 'data-double-submit-lock';
    var OVERLAY_ID = 'tendenci-page-loading';
    var STYLE_ID = 'tendenci-loading-style';
    var nativeSubmit = HTMLFormElement.prototype.submit;

    function isForm(node) {
        return node && node.nodeName === 'FORM';
    }

    function isSubmitControl(control) {
        if (!control || control.disabled) {
            return false;
        }
        var tag = control.tagName;
        if (tag === 'INPUT') {
            var inputType = (control.getAttribute('type') || '').toLowerCase();
            return inputType === 'submit' || inputType === 'image';
        }
        if (tag === 'BUTTON') {
            var buttonType = (control.getAttribute('type') || 'submit').toLowerCase();
            return buttonType === 'submit';
        }
        return false;
    }

    function submitControls(form) {
        var nodes = form.querySelectorAll('button, input[type="submit"], input[type="image"]');
        var controls = [];
        for (var i = 0; i < nodes.length; i++) {
            if (isSubmitControl(nodes[i])) {
                controls.push(nodes[i]);
            }
        }
        return controls;
    }

    function lockControls(form) {
        var controls = submitControls(form);
        for (var i = 0; i < controls.length; i++) {
            controls[i].disabled = true;
            controls[i].setAttribute(MARK, 'true');
        }
    }

    function unlockForm(form) {
        form.removeAttribute(LOCK);
        form.removeAttribute(ASYNC);
        form.removeAttribute(OWNED);
        var controls = form.querySelectorAll('[' + MARK + ']');
        for (var i = 0; i < controls.length; i++) {
            controls[i].disabled = false;
            controls[i].removeAttribute(MARK);
        }
        hideLoading();
    }

    function ensureLoadingStyle() {
        if (document.getElementById(STYLE_ID)) {
            return;
        }
        var style = document.createElement('style');
        style.id = STYLE_ID;
        style.textContent = ''
            + '#' + OVERLAY_ID + '{position:fixed;inset:0;z-index:200000;display:flex;'
            + 'align-items:center;justify-content:center;flex-direction:column;'
            + 'background:rgba(255,255,255,0.78);color:#333;}'
            + '#' + OVERLAY_ID + ' .tendenci-loading-spinner{width:3rem;height:3rem;'
            + 'border:4px solid #d9d9d9;border-top-color:#337ab7;border-radius:50%;'
            + 'animation:tendenci-loading-spin 0.7s linear infinite;}'
            + '#' + OVERLAY_ID + ' p{margin:0.75rem 0 0;font-size:1.125rem;}'
            + '@keyframes tendenci-loading-spin{to{transform:rotate(360deg);}}'
            + '@media (prefers-reduced-motion:reduce){'
            + '#' + OVERLAY_ID + ' .tendenci-loading-spinner{animation:none;}}';
        document.head.appendChild(style);
    }

    function showLoading() {
        if (document.getElementById(OVERLAY_ID)) {
            return;
        }
        ensureLoadingStyle();
        var overlay = document.createElement('div');
        var spinner = document.createElement('div');
        var message = document.createElement('p');
        overlay.id = OVERLAY_ID;
        overlay.setAttribute('role', 'status');
        overlay.setAttribute('aria-live', 'polite');
        spinner.className = 'tendenci-loading-spinner';
        spinner.setAttribute('aria-hidden', 'true');
        message.textContent = 'Loading';
        overlay.appendChild(spinner);
        overlay.appendChild(message);
        document.body.appendChild(overlay);
        document.body.setAttribute('aria-busy', 'true');
    }

    function hideLoading() {
        var overlay = document.getElementById(OVERLAY_ID);
        if (overlay && overlay.parentNode) {
            overlay.parentNode.removeChild(overlay);
        }
        if (document.body) {
            document.body.removeAttribute('aria-busy');
        }
    }

    function rememberSubmitter(form, submitter) {
        if (!submitter || !submitter.name) {
            return;
        }
        var hidden = document.createElement('input');
        hidden.type = 'hidden';
        hidden.name = submitter.name;
        hidden.value = submitter.value;
        form.appendChild(hidden);
    }

    function submitNative(form) {
        nativeSubmit.call(form);
    }

    document.addEventListener('submit', function (event) {
        var form = event.target;
        if (!isForm(form) || form.hasAttribute('data-allow-repeat-submit')) {
            return;
        }
        if (form.getAttribute(LOCK) === 'true') {
            event.preventDefault();
            event.stopPropagation();
            return;
        }
        form.setAttribute(LOCK, 'true');
        // Bubble listeners may call stopPropagation (jQuery's `return false`),
        // so release a cancelled submit from here if nobody claims it.
        window.setTimeout(function () {
            if (form.getAttribute(LOCK) !== 'true' || form.hasAttribute(OWNED)) {
                return;
            }
            if (form.hasAttribute(ASYNC)) {
                showLoading();
                lockControls(form);
                return;
            }
            if (event.defaultPrevented) {
                form.removeAttribute(LOCK);
            }
        }, 0);
    }, true);

    document.addEventListener('submit', function (event) {
        var form = event.target;
        if (!isForm(form) || form.hasAttribute('data-allow-repeat-submit')) {
            return;
        }
        if (form.getAttribute(LOCK) !== 'true') {
            return;
        }

        if (event.defaultPrevented) {
            if (form.hasAttribute(ASYNC)) {
                showLoading();
                lockControls(form);
            } else {
                form.removeAttribute(LOCK);
            }
            return;
        }

        event.preventDefault();
        form.setAttribute(OWNED, 'true');
        showLoading();
        rememberSubmitter(form, event.submitter);
        lockControls(form);
        // Two frames let the spinner paint before the browser navigates.
        requestAnimationFrame(function () {
            requestAnimationFrame(function () {
                submitNative(form);
            });
        });
    }, false);

    document.addEventListener('tendenci:submit-cancelled', function (event) {
        var form = event.target;
        if (isForm(form)) {
            unlockForm(form);
        }
    });

    window.addEventListener('pageshow', function (event) {
        if (!event.persisted) {
            return;
        }
        var forms = document.querySelectorAll('form[' + LOCK + ']');
        for (var i = 0; i < forms.length; i++) {
            unlockForm(forms[i]);
        }
    });
}());
