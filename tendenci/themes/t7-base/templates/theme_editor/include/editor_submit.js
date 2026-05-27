$("#editorForm").on("submit", function() {
    var data = {'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'content': editor.getCode()};
    $.ajax({
        type: 'post',
        dataType: 'json',
        data: data,
        url: '{% url "theme_editor.editor" %}?file={{ current_file_path }}&theme_edit={{ current_theme }}',
        success: function(response) {
            $('#save_message').text(response.message);
            $('#save_message').addClass('success');
            $('#save_message').show();
            setTimeout(function () {
                $('#save_message').fadeOut();
            }, 5000);
            if (response.status === 'FAIL') {
                $('#save_message').removeClass('success');
                $('#save_message').addClass('error');
            }
        },
        error: function(xhr, status, error) {
            // Handle errors
            console.error(error);
            const contentType = xhr.getResponseHeader('Content-Type');
            if (contentType && contentType.indexOf('application/json') == -1){
				console.log("Content-Type does not indicate JSON:", contentType);
				window.location.reload();
	
			}
            
        }
    });
    return false;
});
