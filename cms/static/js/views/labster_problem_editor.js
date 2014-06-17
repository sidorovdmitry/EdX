define(["jquery", "underscore", "gettext", "codemirror", "js/views/feedback_notification", "js/views/baseview",
        "js/views/metadata", "js/collections/metadata", "jquery.inputnumber"],
    function ($, _, gettext, CodeMirror, NotificationView, BaseView, MetadataView, MetadataCollection) {

        var LabsterProblemEditor = BaseView.extend({

            initialize: function() {
                BaseView.prototype.initialize.call(this);
            },

            render: function() {
                this.initializeEditors();
                return this;
            },

            initializeEditors: function() {
                var textarea = $(".xblock-editor").find("textarea")[0];
                this.codeMirror = CodeMirror.fromTextArea(textarea, {
                    mode: "application/json", 
                    lineNumbers: false, 
                    lineWrapping: false});

                if (this.problem) {
                    this.codeMirror.doc.setValue(this.problem.content_xml);
                }
            },

            save: function(http_method, callback) {
                var content_xml = this.codeMirror.doc.getValue();
                this.problem.content_xml = content_xml;

                $.ajax({
                    type: http_method,
                    url: this.problem_url,
                    contentType: "application/json",
                    dataType: "json",
                    data: JSON.stringify(this.problem),
                    success: function(response) {
                        if (callback) {
                            callback(response);
                        }
                    }
                });
            }

        });

        return LabsterProblemEditor;
    }
);
