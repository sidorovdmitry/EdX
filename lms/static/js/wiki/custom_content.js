$(function() {
    var source = $('#id_content');
    var mce = $('<textarea/>');
    mce.attr('id', "content_html");
    mce.val(marked(source.val()));
    source.after(mce);
    source.hide();

    tinymce.init({
        selector: "textarea#content_html",
        theme: "modern",
        // width: 814,
        // height: 300,
        plugins: [
            "image autolink link"
        ],
        image_dimensions: false,
        image_description: false,
        menubar : false,
        toolbar: "formatselect bold italic underline strikethrough bullist numlist blockquote link unlink image",
        block_formats: "Paragraph=p;Preformatted=pre;Header 1=h1;Header 2=h2;Header 3=h3",
        setup: function(ed) {
            var _timer = null;
            var buildMarkdown = function() {
                // cancel the setTimeout if the function is called again
                // prevent multiple call
                if (_timer != null) {
                    clearTimeout(_timer);
                }

                _timer = setTimeout(function() {
                    var content_md = toMarkdown(ed.getContent());
                    source.val(content_md);
                }, 200);
            };

            ed.on('keyup', function(e) {
                buildMarkdown();
            });

            ed.on('blur', function(e) {
                buildMarkdown();
            });

            ed.on('focus', function(e) {
                buildMarkdown();
            });

            ed.on('SetContent', function(e) {
                buildMarkdown();
            });
        }
    }); 
});
