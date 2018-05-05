var filepicker;

function previewFile() {
    var preview = $('img#submission_preview');
    var file = filepicker[0].files[0];
    var reader = new FileReader();

    reader.onloadend = function () {
        preview.attr('src', reader.result);
    };

    if (file) {
        reader.readAsDataURL(file);
        $("#file_drop_wrapper").addClass('fileChosen');
        $("#submission_info").show();
        $("#drop_file_info").hide();
    } else {
        preview.attr('src', no_img);
    }
}

$(function() {
    filepicker = $('input[type=file]');

    filepicker.on('change', function() {
        previewFile();
    });
});
