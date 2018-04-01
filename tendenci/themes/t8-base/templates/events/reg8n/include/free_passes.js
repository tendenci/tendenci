$(document).ready(function () {

    $('button.fp_chk_btn').click(function(){
        var $this = $(this);
        var registrant_form = $this.closest('.registrant-form');
        var id = parseInt($(registrant_form).find('.item-counter').html()) - 1;
        var email = $(registrant_form).find('#id_registrant-' + id + '-email_0').val();
        var member_number = $(registrant_form).find('#id_registrant-' + id + '-memberid').val();
        if (member_number == undefined ){
            member_number = '';
        }
        if (email==''){
            alert("Please fill out the email field then try again!");
            return false;
        }else{

            $.post(
                '{% url "event.check_free_pass_eligibility" %}',
                {
                    'email': email,
                    'member_number': member_number,
                },
                function(data, textStatus, jqXHR){
                    json = $.parseJSON(data);
                    //alert(json['message'])
                    var fp_message = $(registrant_form).find('.free-pass-message');
                    $(fp_message).css('padding-left', '2em');
                    $(fp_message).css('color', '#777');
                    if (!json["is_corp_member"] || !json['pass_avail']){
                        $(registrant_form).find('.fp-field').hide();
                        if (!json["is_corp_member"]){
                            $(fp_message).html('Not a corporate member');
                        }
                        if (!json['pass_avail']){
                            $(fp_message).html('No free pass available');
                        }
                    } else {
                        $(registrant_form).find('.fp-field').show();
                        var msg = json['pass_avail'] + ' free pass(es) available ';
                        msg = msg.concat('for corporate "' + json['corp_name'] + '" ');
                        msg = msg.concat(' (total: ' + json['pass_total'] + ', ');
                        msg = msg.concat('used: ' + json['pass_used'] + ').<br /> ');
                        msg = msg.concat("You're welcome to use one.<br />");
                        msg = msg.concat('*** Note that - free passes are based on "first come, first served" policy.<br />');
                        msg = msg.concat('Thus, they may not be available upon submission.');
                        $(fp_message).html(msg);

                    }
                });

            return false;
        }
    });

    $('.fp-field input[type=checkbox]').each(function() {
        var $this = $(this);
        var fp_field = $(this).closest('.fp-field');

            update_fp_item($this);
            if ($this.is(':checked')){
                   $(fp_field).show();
            }else{
                $(fp_field).hide();
            }
         });

        $('.fp-field input[type=checkbox]').click(function(){
         update_fp_item($(this));
    });

    function update_fp_item(fp_item){
         var $this = $(fp_item);
         var registrant_form = $this.closest('.registrant-form');
         var id = parseInt($(registrant_form).find('.item-counter').html()) - 1;
         // update summary
         var item_price = $('#summary-registrant-' + id).find('.item-price');
         var item_img = '<span class="free-pass-img">&nbsp;</span>';
         if ($this.is(':checked')){
             $(item_price).addClass('free-pass-price');
             $(item_price).after(item_img);
         }else{
             $(item_price).removeClass('free-pass-price');
             $(item_price).closest('td').find('.free-pass-img').remove();
         }
         updateSummaryTotal();
    }
    });