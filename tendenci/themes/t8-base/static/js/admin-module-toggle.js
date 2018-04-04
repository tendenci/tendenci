django.jQuery('document').ready(function() {
    var path_name = window.location.pathname
    if (path_name == '/admin/') {
        var hidden_modules = [
            'Auth',
            'Avatar',
            'Djcelery',
            'Payments',
            'Photos',
            'Plugin_Builder',
            'Social_Auth',
            'Sites',
            'Tagging',
            'Tastypie',
            'User_Groups'
        ];
        var content_main = django.jQuery('#content-main');
        var modules = content_main.find('div.module');

        function hide_modules() {
            modules.each(function() {
                var module = django.jQuery(this);
                var section = module.find('a.section');
                var caption = section.html();
                for (var i in hidden_modules) {
                    if (hidden_modules[i] == caption) {
                        module.hide();
                        module.css("background-color", "#f3d4d4");
                    }
                }
            });
        }

        function show_modules () {
            modules.each(function() {
                var module = django.jQuery(this);
                var section = module.find('a.section');
                if (module.css("display") == "none")
                    module.show();
            });
        }

        function toggle_modules(link) {
            var status = link.attr('data-show');

            if (status == 'false') {
                show_modules();
                link.attr('data-show', 'true');
                link.html(link.html().replace('Show', 'Hide'));
            } else {
                hide_modules();
                link.attr('data-show', 'false');
                link.html(link.html().replace('Hide', 'Show'));
            }
        }

        django.jQuery('a.module-toggle').live('click', function() {
            toggle_modules(django.jQuery(this));
            return false;
        });

        hide_modules();
    }
});
