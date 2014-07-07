$("#editorForm").submit(function() {
    var data = {'csrfmiddlewaretoken': $('input[name="csrfmiddlewaretoken"]').val(),
                'content': editor.getCode(),
                'rf_path': $('input#id_rf_path').val()};
    $.ajax({
        type: 'post',
        dataType: 'json',
        data: data,
        url: '{% url theme_editor.editor %}?file={{ current_file_path }}&theme_edit={{ current_theme }}',
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
        }
    });
    return false;
});
