function gplusHelpTextsInit(siteURL) {
    var gauthor_options = {'content': 'Individual Author is for personal attribution and is recommended for Articles or News.', 'trigger':'hover'};
    $('.gauthor-info').popover(gauthor_options);

    var gpub_options = {'content': 'Publisher is for company attribution and is recommended for Pages.', 'trigger':'hover'};
    $('.gpub-info').popover(gpub_options);

    var gauthor_help = '<p>1. Add a reciprocal link back from your profile to the site(s) you just updated.</p><p>2. Edit the <a href="http://plus.google.com/me/about/edit/co" target="_blank">Contributor To section</a>.</p><p>3. In the dialog that appears, click Add custom link, and then enter <strong>' + siteURL +'</strong>.</p><p>4. If you want, click the drop-down list to specify who can see the link.</p><p>5. Click Save.</p>';
    var gauthor_help_options = {'html': true, 'content': gauthor_help};
    $('.gauthor-help').popover(gauthor_help_options);

    var gpub_help = '<p>1. Make sure you are using <a href="https://support.google.com/plus/answer/1713328" target-"_blank">Google+ as your page</a>.</p><p>2. Click Profile on the left.</p><p>3. On the "About" tab, click the Link website button next to your website URL <strong>' + siteURL +'</strong>.</p>';
    var gpub_help_options = {'html': true, 'content': gpub_help};
    $('.gpub-help').popover(gpub_help_options);

    $('html').click(function(e) {
        var target = $(e.target);
        if (!target.is('.popover, .popover-title, .popover-content')) {
            if (!target.is('.gauthor-help')) {
                $('.gauthor-help').popover('hide');
            }
            if (!target.is('.gpub-help')) {
                $('.gpub-help').popover('hide');
            }
        }
    });
}
