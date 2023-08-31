{% block extra_body %}
<!-- For Component and Client View -->
<script src="https://source.zoom.us/2.15.2/lib/vendor/react.min.js"></script>
<script src="https://source.zoom.us/2.15.2/lib/vendor/react-dom.min.js"></script>
<script src="https://source.zoom.us/2.15.2/lib/vendor/redux.min.js"></script>
<script src="https://source.zoom.us/2.15.2/lib/vendor/redux-thunk.min.js"></script>
<script src="https://source.zoom.us/2.15.2/lib/vendor/lodash.min.js"></script>

<!-- For Component View -->
<script src="https://source.zoom.us/2.15.2/zoom-meeting-embedded-2.15.2.min.js"></script>

<script type="text/javascript">
    function startMeeting() {
        console.log("starting...")
    const client = ZoomMtgEmbedded.createClient()
        console.log("client created...")
    let meetingSDKElement = document.getElementById('meetingSDKElement')

        console.log("init....")
    client.init({
        zoomAppRoot: meetingSDKElement,
        language: 'en-US',
        customize: {
            video: {
                popper: {
                    placement: 'top'
                },
                isResizable: true,
                viewSizes: {
                    default: {
                        width: 1000,
                        height: 600
                    },
                    ribbon: {
                        width: 300,
                        height: 700
                    }
                }
            }
        }
    })

        console.log("joining....")

        let meetingConfig = JSON.parse('{{ event.zoom_meeting_config|safe }}');
        client.join({
            ...meetingConfig,
            userName:  '{{ registrant_user.username }}',
            userEmail: '{{ registrant_user.email }}'
      });
        console.log("joined!")
}

</script>
{% endblock %}
