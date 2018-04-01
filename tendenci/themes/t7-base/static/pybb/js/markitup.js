$(function() {
    if(window.pybb && window.pybb.get_markitup_settings){
        var mySettings = window.pybb.get_markitup_settings();
        $('textarea:not([class="no-markitup"])').markItUp(mySettings);
        $('#emoticons a').click(function() {
            var emoticon = $(this).attr("title");
            $.markItUp({replaceWith: emoticon});
            return false;
        });
    }
});
