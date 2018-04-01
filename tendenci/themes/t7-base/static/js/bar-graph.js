// reference http://www.tuttoaster.com/creating-bar-graphs-using-jquery-ui/
(function ($) {
    $.fn.graph = function(options){
        var defaults = {height:200,width:200,data:'',categories:'',legend:"Graph"};
        var options = $.extend(defaults, options);

        var root = $(this).addClass("ui-widget-content");
        root.wrap("<div class=' ui-widget ' />");
        var parent = root.parent();

        parent.css({height:options.height,width:options.width});
        root.css("position","relative");

        var i=0,max_val=0,scale,temp,w;
        for(i=0; i<options.data.length; i++) {
            if(options.data[i]>=max_val)
                max_val = options.data[i];
        }
        scale = options.height/options.data.length;
        i=options.height;
        var bg = jQuery("<div />",{ css:{height:scale - 1 }  }).addClass("ui-helper-reset ui-widget-bg");
        var bar = jQuery("<div />",{ css:{width:width}  }).addClass("ui-helper-reset ui-state-active ui-widget-bar");
        var width = Math.floor((options.width-150)/options.data.length - (options.categories.length/1.5));

        var counter = 0;
        while(i >= 0) {
            temp = bg.clone().html((max_val - counter).toFixed(2));
            root.append(temp);
            i = i - scale;
            counter = counter + max_val/options.data.length;
        }

        w= 70;
        for(i=0; i<options.categories.length; i++) {
            temp =  Math.floor(options.data[i]/max_val * options.height );
            root.append(bar.clone().css({height:temp,left:w,width:width}).html(options.categories[i]));
            w = w + width + 40;
        }
    };
})(jQuery);
