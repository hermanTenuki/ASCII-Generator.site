$(document).ready(function () {
    let generated_image_ascii = {};
    let generated_text_ascii = {};

    // Put jQuery selector to display
    function animate_fade_in(elem, speed = 750, delay = 0) {
        setTimeout(function () {
            elem.css({'opacity': 0});
            elem.removeClass('hide');
            elem.animate({'opacity': 1}, speed);
        }, delay);
    }

    // Put jQuery selector to hide
    function animate_fade_out(elem, speed = 750, delay = 0, delete_after = false) {
        elem.delay(delay).animate({'opacity': 0}, speed, 'swing', function () {
            if (delete_after) {
                elem.remove();
            } else {
                elem.addClass('hide');
                elem.css({'opacity': 1});
            }
        });
    }

    // Switch url link depending on what input type is selected ("/" for img, "t/" for txt)
    function switch_url_by_input(mode = '') {
        const root_url_href = window.location.href.replace('/t/', '/');
        if (mode === 'img') {
            window.history.replaceState({}, 'img2ascii', root_url_href)
        } else if (mode === 'txt') {
            window.history.replaceState({}, 'txt2ascii', 't/')
        }
    }

    // Display input method depending on what text in header is underlined
    function switch_input_type() {
        const input_type_switcher_all_p = $('header .switcher').find('p');
        const input_type_img = $('section.index .img2ascii-input');
        const input_type_txt = $('section.index .txt2ascii-input');
        input_type_img.addClass('hide');
        input_type_txt.addClass('hide');
        if ($(input_type_switcher_all_p.get(0)).hasClass('chosen')) {
            animate_fade_in(input_type_img);
            switch_url_by_input('img')
        } else if ($(input_type_switcher_all_p.get(1)).hasClass('chosen')) {
            animate_fade_in(input_type_txt);
            switch_url_by_input('txt')
        }

    }

    // Switch underline on p's in header
    $('header .switcher').on('click', 'p', function () {
        if ($('header .switcher').find('.chosen').length > 0) {
            if ($(this).hasClass('chosen') === false) {
                $('header .switcher').find('p').each(function () {
                    $(this).toggleClass('chosen')
                });
                switch_input_type();
            }
        }
    });

    // Switch underline on p's in header (if clicked on small text below input method)
    $('section.index').on('click', 'p.ps-tiny', function () {
        $('header .switcher').find('p').each(function () {
            $(this).toggleClass('chosen')
        });
        switch_input_type();
    });

    // Display and hide language switch window if language clicked in footer
    $('footer').on('click', '.language-switcher', function () {
        const language_switcher_window = $('footer .language-switcher .language-switcher-window');
        if (language_switcher_window.hasClass('hide')) {
            animate_fade_in(language_switcher_window, 250);
        } else {
            animate_fade_out(language_switcher_window, 150);
        }
    });

    // Display agreements if 'Agreement - user_agreed_v1' cookie is not found
    if (Cookies.get('Agreement') !== 'user_agreed_v1') {
        animate_fade_in($('.agreements'), 200, 1000);
    }

    // If "I Agree" button is clicked in agreements, hide message and set cookie 'Agreement - user_agreed_v1'
    $('.agreements').on('click', 'input[type=button]', function () {
        Cookies.set('Agreement', 'user_agreed_v1', {expires: 365});
        animate_fade_out($('.agreements'), 0);
    });

    // Send ajax-request for feedback form
    $('section.feedback').on('submit', 'form.feedback-form', function () {
        const cur_elem = $(this);
        cur_elem.find('p.error').remove();

        const placement = cur_elem.offset().top + (cur_elem.height() / 2) - 56;
        cur_elem.find('input[type=submit]').attr('disabled', '');
        $('body').append( // animated loading circle
            '<div class="circle-loader-div" style="top: ' + placement + 'px">\n' +
            '    <div class="circle-loader">\n' +
            '        <div class="checkmark draw"></div>\n' +
            '    </div>\n' +
            '</div>'
        );

        $.ajax({
            url: cur_elem.attr('action'),
            type: 'POST',
            data: cur_elem.serialize(),
            error: function (response) {
                const errors = response.responseJSON['errors'];
                let error_obj = errors['text'];
                if (error_obj) {
                    for (let key in Object.keys(error_obj)) {
                        cur_elem.find('#id_text').after(
                            '<p class="error">' + error_obj[key] + '</p>'
                        )
                    }
                }
                error_obj = errors['email'];
                if (error_obj) {
                    for (let key in Object.keys(error_obj)) {
                        cur_elem.find('#id_email').after(
                            '<p class="error">' + error_obj[key] + '</p>'
                        )
                    }
                }
                error_obj = errors['captcha'];
                if (error_obj) {
                    for (let key in Object.keys(error_obj)) {
                        cur_elem.find('#id_captcha').after(
                            '<p class="error">' + error_obj[key] + '</p>'
                        )
                    }
                }
                error_obj = errors['agreement'];
                if (error_obj) {
                    for (let key in Object.keys(error_obj)) {
                        cur_elem.find('#id_agreement + label').after(
                            '<p class="error">' + error_obj[key] + '</p>'
                        )
                    }
                }
                $('.circle-loader').css({'border-color': '#ff2635'});
                animate_fade_out($('.circle-loader-div'), 250, 250, true);
            },
            success: function (response) {
                cur_elem[0].reset();
                $('.circle-loader').toggleClass('load-complete');
                $('.circle-loader .checkmark').toggle();
                animate_fade_out($('.circle-loader-div'), 500, 1000, true);
            },
            complete: function (response) {
                cur_elem.find('input[type=submit]').removeAttr('disabled');
                grecaptcha.reset();
            }
        });
        return false
    });

    // Ajax image uploader
    let fileUploadEnabled = true;

    const init_uploader = function () {
        const fileInputElement = document.querySelector('.js-file__input');
        const fileDropZone = document.querySelector('.js-dropzone');

        // Prevents the default behavior of refresh
        // Force click on the input element
        document.querySelector('.file__input-label-button').addEventListener('click', function (e) {
            e.preventDefault();
            fileInputElement.click();
        });

        // Handle Creating Elements for the files using the Browse button
        fileInputElement.addEventListener('change', function (e) {
            if (fileUploadEnabled) {
                const validatedFiles = fileValidation([...fileInputElement.files]);
                if (validatedFiles[0]) {
                    uploadFile(validatedFiles[0]);
                }
            }
        });

        // Prevents default behavior of automatically opening the file
        fileDropZone.addEventListener('dragover', function (e) {
            $(fileDropZone).addClass('hovered');
            e.preventDefault();
        });

        fileDropZone.addEventListener('dragenter', function() {
            $(fileDropZone).addClass('hovered');
        });

        fileDropZone.addEventListener('dragleave', function() {
            $(fileDropZone).removeClass('hovered');
        });

        // Gets node element list of files Converts them to a list of Arrays
        // Then calls createFileDOMNode to create DOM Element of the files
        fileDropZone.addEventListener('drop', function (e) {
            e.preventDefault();
            if (fileUploadEnabled) {
                const unvalidatedFiles = getArrayOfFileData([...e.dataTransfer.items]);
                const validatedFiles = fileValidation(unvalidatedFiles);
                if (validatedFiles[0]) {
                    uploadFile(validatedFiles[0]);
                }
            }
        });
    };

    // Upload File ajax request
    const uploadFile = function (file) {
        fileUploadEnabled = false;
        const fileDropZone = $('section.index .js-dropzone');
        const fileUploadModal = $('section.index .file-upload__modal');
        const asciiImageOutput = $('section.index .ascii-image-output');
        const csrf_token = fileDropZone.find('input[name="csrfmiddlewaretoken"]').val();
        let data = new FormData();
        data.append('img', file);

        const placement = fileDropZone.offset().top - 25;
        $('body').append( // animated loading circle
            '<div class="circle-loader-div" style="top: ' + placement + 'px">\n' +
            '    <div class="circle-loader">\n' +
            '        <div class="checkmark draw"></div>\n' +
            '    </div>\n' +
            '</div>'
        );

        $.ajax({
            url: fileDropZone.attr('action'),
            type: 'POST',
            data: data,
            processData: false,
            contentType: false,
            headers: {
                'X-CSRFToken': csrf_token,
            },
            error: function (response) {
                $('.circle-loader').css({'border-color': '#ff2635'});
                animate_fade_out($('.circle-loader-div'), 250, 250, true);
            },
            success: function (response) {
                $('.circle-loader').toggleClass('load-complete');
                $('.circle-loader .checkmark').toggle();
                animate_fade_out($('.circle-loader-div'), 500, 1000, true);
                const arts = response.arts;
                generated_image_ascii = {};
                for (let i in arts) {
                    generated_image_ascii[i] = arts[i].replace(new RegExp("&" + "#" + "x27;", "g"), "'");
                }
                change_font_size_on_art(true);
                update_displayed_image(file, response.file_name);
                update_displayed_image_options(response);

                fileUploadModal.addClass('hide');
                asciiImageOutput.removeClass('hide');
                update_displayed_image_art();
            },
            complete: function (response) {
                fileUploadEnabled = true;

            }
        });
    };

    // Validates each file that it is the format we accept
    // Then pushes the validated file to a new array
    const fileValidation = function (files) {
        const errMessageOutput = document.querySelector('.file-upload__error');
        const validatedFileArray = [];
        const supportedExts = ['png', 'jpg', 'jpeg', 'bmp', 'gif', 'ico', 'webp'];
        files.forEach(file => {
            const ext = getFileExtension(file);
            if (file.size > 5242880) {
                let errMessage = 'Maximum size is 5 MB.';
                errMessageOutput.style.display = 'block';
                errMessageOutput.textContent = errMessage;
            } else if (supportedExts.indexOf(ext) === -1) {
                let errMessage =
                    'Supported formats are: .png, .jpg, .bmp, .gif, .ico, .webp.';
                errMessageOutput.style.display = 'block';
                errMessageOutput.textContent = errMessage;
                // return '';
            } else {
                errMessageOutput.style.display = 'none';
                validatedFileArray.push(file);
            }
        });
        return validatedFileArray;
    };

    // Returns an array of the file data
    const getArrayOfFileData = function (files) {
        const fileDataArray = [];
        files.forEach(file => {
            if (file.kind === 'file') {
                fileDataArray.push(file.getAsFile());
            }
        });
        return fileDataArray;
    };

    // Returns the files type extension
    const getFileExtension = function (file) {
        return file.name.split('.').pop();
    };

    // Truncates a string if too long
    const truncateString = function (str, num) {
        if (str.length > num) {
            return str.slice(0, num) + '...';
        } else {
            return str;
        }
    };

    init_uploader();

    // Update displayed options on ascii art
    function update_displayed_image_options(response_dict) {
        const options_container = $('section.index .ascii-image-output .options_container');
        options_container.find('#option_num_cols').val(response_dict.num_cols);
        options_container.find('#option_brightness').val(response_dict.brightness);
        options_container.find('#option_contrast').val(response_dict.contrast);
    }

    // Update displayed image on ascii art
    function update_displayed_image(file, file_name) {
        const reader = new FileReader();
        const image = $('section.index .ascii-image-output .image img');
        const art_div = $('section.index .ascii-image-output .ascii-art');
        reader.onload = function (e) {
            image.attr('src', e.target.result);
        };
        reader.readAsDataURL(file);
        image.data('file_name', file_name);
    }

    // Switch image ascii art
    function update_displayed_image_art(adapt=true) {
        const slider_window = $('section.index .ascii-image-output .slider-window');
        const art_div = $('section.index .ascii-image-output .ascii-art');
        art_div.css({
            'letter-spacing': 'unset',
            'line-height': 'unset',
            'transform': 'unset'
        });
        const art_id = $('section.index .ascii-image-output .buttons.second_row .chosen').data('method_id');
        const art = generated_image_ascii[art_id];
        const image = $('section.index .ascii-image-output .image img');
        art_div.text(art);
        // If client is on Chrome, change some styles of second ASCII-art
        if (window.chrome && parseInt(art_id) === 1) {
           art_div.css({
               'letter-spacing': '-0.1em',
               'line-height': '1.2em',
               'transform': 'scale(1.2, 1) translateX(8%)'
           });
            slider_window.css('width', parseFloat(art_div.css('width')) * 1.2 + 6);
        } else {
            slider_window.css('width', parseFloat(art_div.css('width')) + 6);
        }
        slider_window.css('height', parseFloat(art_div.css('height')) + 6);
        // Also update image size
        image.css('width', parseFloat(slider_window.css('width')));
        image.css('height', parseFloat(art_div.css('height')));
        if (adapt) {
            resize_ascii_image_art();
        }
    }

    // Change font-size on image ASCII-art
    function change_font_size_on_art(revert = false, symbol = '?') {
        const art_div = $('section.index .ascii-image-output .ascii-art');
        const span_font_size_number = $('section.index .ascii-image-output span.font-size_number');
        let font_size = parseInt(art_div.css('font-size'));
        if (revert) {
            font_size = 12  // Default font-size
        } else {
            if (symbol === '+') {
                font_size += 1
            } else if (symbol === '-' && font_size > 1) {
                font_size -= 1
            }
        }
        art_div.css('font-size', font_size);
        span_font_size_number.text(font_size);
        update_displayed_image_art();
    }

    $('section.index .ascii-image-output .container_slider').on('click', 'input[type=button]', function () {
        change_font_size_on_art(false, $(this).val());
    });

    // Switch chosen method by clicking on methods numbers
    $('section.index .ascii-image-output .buttons.second_row').on('click', 'div', function () {
        if ($(this).hasClass('chosen') === false) {
            $('section.index .ascii-image-output .buttons.second_row').find('div').removeClass('chosen');
            $(this).addClass('chosen');
            update_displayed_image_art()
        }
    });

    // Invert colors of ascii-image-output
    $('section.index .ascii-image-output').on('click', '.invert_colors img', function () {
        $('section.index .ascii-image-output .slider-window').toggleClass('invert');
    });

    // Copy to clipboard ascii-image-output
    $('section.index .ascii-image-output').on('click', '.copy_to_clipboard img', function () {
        $(this).after('<textarea id="textarea_to_copy" ' +
            'style="opacity: 0; position: absolute; height: 0; width: 0;">' + $('section.index .ascii-image-output .ascii-art').text() + '</textarea>');
        let textarea_to_copy = $('section.index #textarea_to_copy');
        textarea_to_copy.select();
        document.execCommand('copy');
        textarea_to_copy.remove();
        window.getSelection().removeAllRanges();
        document.selection.empty();
    });

    // Bring back image upload form by clicking "New image" btn
    $('section.index .ascii-image-output').on('click', '.new_file img', function () {
        $('section.index .ascii-image-output').addClass('hide');
        animate_fade_in($('section.index .file-upload__modal'));
    });

    // Ajax request to update image with new settings
    $('section.index .ascii-image-output .options_container form').submit(function () {
        const cur_elem = $(this);
        const submit_btn = cur_elem.find('input[type=submit]');
        const cur_ascii_img = $('section.index .ascii-image-output .image img');
        const loading_twirl = $('section.index .ascii-image-output .loading_twirl');
        let data = cur_elem.serialize();
        data += '&file_name=' + cur_ascii_img.data('file_name');
        submit_btn.attr('disabled', '');
        submit_btn.css({'color': 'transparent'});
        animate_fade_in(loading_twirl, 200);


        $.ajax({
            url: cur_elem.attr('action'),
            type: 'POST',
            data: data,
            error: function (response) {
                uploadFile(cur_ascii_img[0].src);
            },
            success: function (response) {
                const arts = response.arts;
                generated_image_ascii = {};
                for (let i in arts) {
                    generated_image_ascii[i] = arts[i].replace(new RegExp("&" + "#" + "x27;", "g"), "'");
                }
                update_displayed_image_art();
                update_displayed_image_options(response);
            },
            complete: function () {
                submit_btn.removeAttr('disabled style');
                animate_fade_out(loading_twirl, 50)
            }
        });
        return false
    });

    // Invert colors of ascii-text-output textarea
    $('section.index .ascii-text-output').on('click', '.invert_colors img', function () {
        $('section.index .ascii-text-output textarea[name="output"]').toggleClass('invert');
    });

    // Copy to clipboard ascii-text-output textarea
    $('section.index .ascii-text-output').on('click', '.copy_to_clipboard img', function () {
        $('section.index .ascii-text-output textarea[name="output"]').select();
        document.execCommand('copy');
        window.getSelection().removeAllRanges();
        document.selection.empty();
    });

    // Update displayed ASCII art in output textarea
    function update_displayed_text_art() {
        const textarea = $('section.index .ascii-text-output textarea[name="output"]');
        const resize_div = $('section.index #ascii-text-output-resize-textarea');
        textarea.text(generated_text_ascii[$('section.index .ascii-text-output #select-method').val()]);
        textarea.css({'width': '100%'});
        resize_div.width(0).css({'width': 'unset', 'max-width': textarea[0].scrollWidth + 2});
        if ($('section.index .wrapper').width() > resize_div.width()) {
            textarea.height(0).height(textarea[0].scrollHeight - 20);
        } else {
            textarea.height(0).height(textarea[0].scrollHeight - 3);
        }


        window.scrollBy(0, document.body.scrollHeight);
    }

    // Choose previous option in selector
    $('section.index .ascii-text-output').on('click', '.back img', function () {
        const selector_elem = $('section.index .ascii-text-output #select-method');
        if (parseInt(selector_elem.val()) > 0) {
            selector_elem.val(parseInt(selector_elem.val()) - 1);
            update_displayed_text_art();
        }
    });

    // Choose next option in selector
    $('section.index .ascii-text-output').on('click', '.forward img', function () {
        const selector_elem = $('section.index .ascii-text-output #select-method');
        if (generated_text_ascii[parseInt(selector_elem.val()) + 1]) {
            selector_elem.val(parseInt(selector_elem.val()) + 1);
            update_displayed_text_art();
        }
    });

    // Randomize option in selector
    $('section.index .ascii-text-output').on('click', '.randomize img', function () {
        const selector_elem = $('section.index .ascii-text-output #select-method');
        const rnd_min = parseInt(selector_elem.find('option').first().val());
        const rnd_max = parseInt(selector_elem.find('option').last().val());
        selector_elem.val(Math.floor(Math.random() * (rnd_max - rnd_min + 1)) + rnd_min);
        update_displayed_text_art();
    });

    // When other method is selected, call update_displayed_text_art
    $('section.index .ascii-text-output #select-method').change(update_displayed_text_art);

    // Text to ASCII ajax request
    $('section.index .txt2ascii-input form.txt2ascii-form').submit(function () {
        const cur_elem = $(this);
        const output_div = $('section.index .ascii-text-output');

        const placement = cur_elem.offset().top + 10;
        cur_elem.find('input[type=submit]').attr('disabled', '');
        $('body').append( // animated loading circle
            '<div class="circle-loader-div" style="top: ' + placement + 'px">\n' +
            '    <div class="circle-loader">\n' +
            '        <div class="checkmark draw"></div>\n' +
            '    </div>\n' +
            '</div>'
        );

        $.ajax({
            url: cur_elem.attr('action'),
            type: 'POST',
            data: cur_elem.serialize(),
            error: function (response) {
                $('.circle-loader').css({'border-color': '#ff2635'});
                animate_fade_out($('.circle-loader-div'), 250, 250, true);
                output_div.addClass('hide');
            },
            success: function (response) {
                const select_elem = output_div.find('#select-method');
                const results = response.results;
                generated_text_ascii = {};
                select_elem.find('option').remove();
                for (let i in results) {
                    select_elem.append('<option value="' + i + '">' + results[i][0] + '</option>');
                    generated_text_ascii[i] = results[i][1].replace(new RegExp("&" + "#" + "x27;", "g"), "'")
                }
                output_div.removeClass('hide');
                update_displayed_text_art();
                $('.circle-loader').toggleClass('load-complete');
                $('.circle-loader .checkmark').toggle();
                animate_fade_out($('.circle-loader-div'), 500, 1000, true);
            },
            complete: function (response) {
                cur_elem.find('input[type=submit]').removeAttr('disabled');
            }
        });
        return false;
    })

    // Screenshot and save image ASCII-art
    $("#button_art_download").click(function () {
        window.scrollTo(0, 0);
        $('.slider-window').addClass("overflowVisible");
        const art_download = $('#art_download');
        const old_font_size = parseInt(art_download.css('font-size'));
        if (old_font_size !== 14) {
            art_download.css({
                'font-size': 14,
                'position': 'fixed',
                'left': 0,
                'top': 0
            });
            update_displayed_image_art(false);
        }
        html2canvas(art_download[0], {
            scrollX: 0,
            scrollY: -window.scrollY
        }).then(function (canvas) {
                theCanvas = canvas;
                canvas.toBlob(function (blob) {
                    saveAs(blob, "ASCII-art.png");
                    $('.slider-window').removeClass("overflowVisible");
                    art_download.css({
                        'font-size': old_font_size,
                        'position': 'absolute'
                    });
                    update_displayed_image_art()
                });
            }
        )
    });


    // ASCII-arts adaptations on resize
    // Can't implement this with just styling
    function resize_ascii_image_art() {
        const art_div = $('section.index .ascii-image-output .ascii-art');
        const font_size = parseInt(art_div.css('font-size'));
        const container_slider_width = $('section.index .ascii-image-output .container_slider').width();
        const wrapper_width = $('section.index .wrapper').width();
        if ((container_slider_width + 100 >= wrapper_width) && (font_size > 2)) {
            change_font_size_on_art(false, '-');
            update_displayed_image_art(true);
        }
    }

    // ^
    window.onresize = function () {
        resize_ascii_image_art();
    }
});