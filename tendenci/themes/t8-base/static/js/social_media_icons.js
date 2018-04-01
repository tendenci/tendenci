$(document).ready(function() {
    $(".social-popup").click(function(e) {
        e.preventDefault();
        var width = 600, height = 400;
        if ($(this).hasClass('social-google')) {
            width = 500;
            height = 450;
        }

        window.open(
            $(this).attr('href'),
            'Social Popup',
            'menubar=no,toolbar=no,resizable=no,scrollbars=no,height=' + height + ',width=' + width
        );
        return false;
    })
});
