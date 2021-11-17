from tendenci.apps.chapters.models import ChapterMembershipApp


def get_notice_token_help_text(notice=None):
    """Get the help text for how to add the token in the email content,
        and display a list of available token.
    """
    help_text = ''
    app = ChapterMembershipApp.objects.current_app()

    # render the tokens
    help_text += '<div>'
    help_text += """
                <div style="margin-bottom: 1em;">
                You can use tokens to display chapter member info or site specific
                information.
                A token is a field name wrapped in
                {{ }} or [ ]. <br />
                For example, token for first_name field: {{ first_name }}.
                Please note that tokens for chapter member number, chapter membership link,
                and expiration date/time are not available until the chapter membership
                is approved.
                </div>
                """

    help_text += '<div id="toggle_token_view"><a href="javascript:;">' + \
                'Click to view available tokens</a></div>'
    help_text += '<div id="notice_token_list">'
    if app:
        help_text += f'<div style="font-weight: bold;">Field Tokens</div>'
        fields = app.fields.filter(display=True).exclude(field_name=''
                                                         ).order_by('position')

        help_text += "<ul>"
        for field in fields:
            help_text += f'<li>{{ {field.field_name} }} - (for {field.label})</li>'
        help_text += "</ul>"
    else:
        help_text += '<div>No field tokens because there is no ' + \
                    'applications.</div>'

    other_labels = [
                    'first_name',
                    'last_name',
                    'email',
                    'username',
                    'member_number',
                    'membership_type',
                    'membership_price',
                    'total_amount',
                    'view_link',
                    'edit_link',
                    'invoice_link',
                    'renew_link',
                    'expire_dt',]

    other_labels += ['site_contact_name',
                    'site_contact_email',
                    'site_display_name',
                    'time_submitted',
                    ]

    help_text += '<div style="font-weight: bold;">Non-field Tokens</div>'
    help_text += "<ul>"
    for label in other_labels:
        help_text += '<li>{{ %s }}</li>' % label
    help_text += "</ul>"
    help_text += "</div>"
    help_text += "</div>"

    help_text += """
                <script>
                    (function($) {
                        $(document).ready(function() {
                            $('#notice_token_list').hide();
                                 $('#toggle_token_view').click(function () {
                                $('#notice_token_list').toggle();
                            });
                        });
                    }(jQuery));
                </script>
                """

    return help_text
