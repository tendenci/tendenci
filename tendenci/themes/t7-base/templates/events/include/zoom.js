{% load base_tags %}
{% block extra_body %}

<script type="text/javascript">
    ZoomMtg.setZoomJSLib('https://source.zoom.us/3.9.0/lib', '/av')
    ZoomMtg.preLoadWasm()
    ZoomMtg.prepareWebSDK()
    // loads language files, also passes any error messages to the ui
    ZoomMtg.i18n.load('en-US')

    document.getElementById('zmmtg-root').style.display = 'block';
    let meetingConfig = JSON.parse('{{ event.zoom_meeting_config|safe }}');

    ZoomMtg.init({
        leaveUrl: '{{ event.get_absolute_url }}',
        disablePreview: true,
        success: (success) => {
            ZoomMtg.join({
                ...meetingConfig,
                userName: '{{ registrant.user.username }}',
                userEmail: '{{ registrant.user.email }}',
                success: (success) => {
                    '{% execute_method registrant "zoom_check_in" event %}'
                },
                error: (error) => {
                    console.log(error);
                },
            })
        },
        error: (error) => {
            console.log(error);
        }
    });

</script>
{% endblock %}
