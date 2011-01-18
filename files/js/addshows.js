$(document).ready(function() {
    $(':checkbox').change(function() {
        // Toggle class of parent label
        var p = $(this).parent();
        if (p.hasClass('checked')) {
            p.addClass('unchecked').removeClass('checked');
        } else {
            p.addClass('checked').removeClass('unchecked');
        }
        
        // Toggle class of grandparent div
        var pp = p.parent();
        if (pp.hasClass('checkedletter')) {
            pp.addClass('normalletter').removeClass('checkedletter');
        } else {
            pp.addClass('checkedletter').removeClass('normalletter');
        }
    });
});