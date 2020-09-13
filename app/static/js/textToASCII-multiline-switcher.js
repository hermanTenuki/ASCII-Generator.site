$(document).ready(function () {
    // Switch multi-line mode in text input function
    function multi_line_mode_change(e, elem = {0: {'checked': false}}) {
        let single_line_text = $('section.index form.txt2ascii-form .single-line_text');
        let multi_line_text = $('section.index form.txt2ascii-form .multi-line_text');

        single_line_text.addClass('hide');
        multi_line_text.addClass('hide');
        if (this.checked || elem[0].checked) {
            multi_line_text.removeClass('hide');
        } else {
            single_line_text.removeClass('hide');
        }
    }

    // Switch multi-line mode in text input when page is loaded (in case of F5)
    multi_line_mode_change(null, $('section.index form.txt2ascii-form #multiple_strings_checkbox'));

    // Switch multi-line mode in text input by changing checkbox
    $('section.index form.txt2ascii-form #multiple_strings_checkbox').change(multi_line_mode_change);
});
