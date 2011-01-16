$(document).ready(function() {
    $(':checkbox').change(function() {
        var p = $(this).parent();
        if (p.hasClass('checked')) {
            p.removeClass('checked').addClass('unchecked');
        } else {
            p.removeClass('unchecked').addClass('checked');
        }
    });
});