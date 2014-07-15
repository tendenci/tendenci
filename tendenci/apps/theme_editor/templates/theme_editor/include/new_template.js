$(function() {
    var tname = $( "#tname" ),
    allFields = $( [] ).add( tname ),
    tips = $( ".validateTips" );
    $('#create-tform').css({'display': 'none'});

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

    $('#create-tform').dialog({
        autoOpen: false,
        height: 300,
        width: 450,
        modal: true,
        buttons: {
            "Create a template": function() {
                var $this = $(this);
                var is_valid = true;
                allFields.removeClass( "ui-state-error" );
                is_valid = is_valid && check_length( tname, "template name", 3, 16 );
                is_valid = is_valid && check_regexp( tname, /^[a-z]([0-9a-z_-])+$/, "Template name may consist of a-z, 0-9, underscores, dashes, begin with a letter." );
                if ( is_valid ) {
                    // ajax submit form
                    $.post(
                        '{% url theme_editor.create_new_template %}',
                        {
                            'template_name': tname.val()
                        },
                        function(data, textStatus, jqXHR){
                            json = $.parseJSON(data);
                            if (json["created"]){
                                $this.dialog( "close" );
                                // redirect
                                location = "{% url theme_editor.editor%}?file=templates/" +
                                            json["template_name"];
                            }else{
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

    $('.new-template-btn').click(function(){
        $('#create-tform').dialog('open');
        $('.ui-dialog-buttonset .ui-state-default').first()
                .css({'background': 'none'})
                .css({'background-color': '#A84524'})
                .css({'color': '#ffffff'});
    });

});