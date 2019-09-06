(function ($) {
    $.fn.selectChain = function (options) {
        var defaults = {
            key: "id",
            value: "label"
        };

        var settings = $.extend({}, defaults, options);

        if (!(settings.target instanceof $)) settings.target = $(settings.target);

        return this.each(function () {
            var $$ = $(this);

            $$.on("change", function () {
                var data = null;
                if (typeof settings.data == 'string') {
                    data = settings.data + '&' + this.name + '=' + $$.val();
                } else if (typeof settings.data == 'object') {
                    data = settings.data;
                    data[this.name] = $$.val();
                } else {
                    data = this.name + '=' + $$.val();
                }

                settings.target.empty();

                $.ajax({
                    url: settings.url,
                    data: data,
                    type: (settings.type || 'get'),
                    dataType: 'json',
                    success: function (j) {
                        var options = [], i = 0, o = null;
                        for (i = 0; i < j.length; i++) {
                            // required to get around IE bug (http://support.microsoft.com/?scid=kb%3Ben-us%3B276228)
                            o = document.createElement("OPTION");
                            o.value = typeof j[i] == 'object' ? j[i][settings.key] : j[i];
                            o.text = typeof j[i] == 'object' ? j[i][settings.value] : j[i];
                            settings.target.get(0).options[i] = o;
                        }

			// hand control back to browser for a moment
			setTimeout(function () {
			    settings.target
                                .find('option:first')
                                .attr('selected', 'selected')
                                .parent('select')
                                .trigger('change');
			}, 0);
                    },
                    error: function (xhr, desc, er) {
                        // add whatever debug you want here.
			alert("an error occurred");
                    }
                });
            });
        });
    };
})(jQuery);
