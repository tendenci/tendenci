$(function() {
    var themeName = $( "#theme-name" ),
    allFields = $( [] ).add( themeName ),
    tips = $( ".validateTips" ),
    url = null;
    $('#theme-name-form').css({'display': 'none'});

    function update_tips( t ) {
        tips
        .text( t )
        .addClass( "ui-state-highlight" );
        setTimeout(function() {
        tips.removeClass( "ui-state-highlight", 1500 );
        }, 1500 );
    }
    function check_length( o, n, min, max ) {
        if ( o.val().length > max || o.val().length < min ) {
            o.addClass( "ui-state-error" );
            if (o.val().length == 0){
                update_tips( n + " cannot be blank." );
            }else{
                update_tips( "Length of " + n + " must be between " +
            min + " and " + max + "." );
            }

            return false;
        } else {
            return true;
        }
    }
    function check_regexp( o, regexp, n ) {
        if ( !( regexp.test( o.val() ) ) ) {
            o.addClass( "ui-state-error" );
            update_tips( n );
            return false;
        } else {
            return true;
        }
    }

    $('#theme-name-form').dialog({
        autoOpen: false,
        height: 300,
        width: 450,
        modal: true,
        buttons: {
            Save: function() {
                var $this = $(this);
                var is_valid = true;
                allFields.removeClass( "ui-state-error" );
                is_valid = is_valid && check_length( themeName, "theme name", 3, 64 );
                is_valid = is_valid && check_regexp( themeName, /^[a-z]([0-9a-z_-])+$/, "Template name must begin with a letter and contain only a-z, 0-9, underscores, and dashes." );
                if ( is_valid ) {
                    // ajax submit form
                    var newTheme = themeName.val();
                    $.post(url,
                        {
                            'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                            'theme_name': newTheme
                        },
                        function(data, textStatus, jqXHR){
                            json = JSON.parse(data);
                            if (json["success"]){
                                $this.dialog( "close" );
                                // redirect
                                location = '{% url "theme_editor.editor" %}?theme_edit='+newTheme;
                            } else {
                                update_tips(json["err"]);
                            }
                        });
                }
            },
            Cancel: function() {
                $(this).dialog( "close" );
                }
            },
        close: function() {
            allFields.val( "" ).removeClass( "ui-state-error" );
        }
    });

    $('.copy-theme-btn').on("click", function(){
        url = '{% url "theme_editor.theme_copy" %}?theme_edit={{ current_theme }}';
        $('#theme-name-form').dialog({title: 'Copy to new theme'});
        $('#theme-name-form').dialog('open');
        $('.ui-dialog-buttonset .ui-state-default').first()
                .css({'background': 'none'})
                .css({'background-color': '#A84524'})
                .css({'color': '#ffffff'});
    });
    $('.rename-theme-btn').on("click", function(){
        url = '{% url "theme_editor.theme_rename" %}?theme_edit={{ current_theme }}';
        $('#theme-name-form').dialog({title: 'Rename theme'});
        $('#theme-name-form').dialog('open');
        $('.ui-dialog-buttonset .ui-state-default').first()
                .css({'background': 'none'})
                .css({'background-color': '#A84524'})
                .css({'color': '#ffffff'});
    });

});
