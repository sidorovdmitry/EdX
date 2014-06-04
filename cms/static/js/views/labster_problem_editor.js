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

                this.codeMirror.doc.setValue(this.problem.content_xml);
            },

            save: function(callback) {
                var content_xml = this.codeMirror.doc.getValue();
                this.problem.content_xml = content_xml;

                $.ajax({
                    type: "PUT",
                    url: this.problem_url,
                    contentType: "application/json",
                    dataType: "json",
                    data: JSON.stringify(this.problem),
                    success: function(response) {
                        callback();
                    }
                });

                // var xblockInfo = this.model,
                //     data,
                //     saving;
                // data = this.getXModuleData();
                // if (data) {
                //     saving = new NotificationView.Mini({
                //         title: gettext("Saving&hellip;")
                //     });
                //     saving.show();
                //     return xblockInfo.save(data).done(function() {
                //         var success = options.success;
                //         saving.hide();
                //         if (success) {
                //             success();
                //         }
                //     });
                // }
            }

        });

        return LabsterProblemEditor;
    }
);
