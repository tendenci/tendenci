function pybb_delete_post(url, post_id, confirm_text) {
    if (!confirm(confirm_text))
        return false;
    $.ajax({
        url: url,
        type: 'POST',
        dataType: 'text',
        success: function (data, textStatus) {
            if (data.length > 0) {
                window.location = data;
            } else {
                $("#" + post_id).slideUp();
            }
        }
    });
}

jQuery(function ($) {
    function getSelectedText() {
        if (document.selection) {
            return document.selection.createRange().text;
        } else {
            return window.getSelection().toString();
        }
    }

    var textarea = $('#id_body');

    if (textarea.length > 0) {
        $('.quote-link').on('click', function (e) {
            e.preventDefault();
            var url = $(this).attr('href');
            $.get(
                url,
                function (data) {
                    if (textarea.val())
                        textarea.val(textarea.val() + '\n');
                    textarea.val(textarea.val() + data);
                    window.location.hash = '#id_body';
                }
            );
        });

        $('.quote-selected-link').on('click', function (e) {
            if (!window.pybb.markup) {
                return true;
            }
            e.preventDefault();
            var selectedText = getSelectedText();
            if (selectedText != '') {
                if (textarea.val())
                    textarea.val(textarea.val() + '\n');
                var username = '';
                if ($(this).closest('.post-row').length == 1 &&
                    $(this).closest('.post-row').find('.post-username').length == 1) {
                    username = $.trim($(this).closest('.post').find('.post-username').text());
                }
                textarea.val(textarea.val() + window.pybb.markup.quote(selectedText, username));
                window.location.hash = '#id_body';
            }
        });

        $('.post-row .post-username').on('click', function (e) {
            if (window.pybb.markup && e.shiftKey) {
                e.preventDefault();
                var username = $.trim($(this).text());
                if (textarea.val())
                    textarea.val(textarea.val() + '\n');
                textarea.val(textarea.val() + window.pybb.markup.username(username));
                window.location.hash = '#id_body';
            }
        });
    }
});
