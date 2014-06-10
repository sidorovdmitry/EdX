define(["underscore", "jquery", "js/views/modals/base_modal", "js/views/labster_problem_editor"],
    function(_, $, BaseModal, LabsterProblemEditorView) {
        var EditProblemModal = BaseModal.extend({
            events: {
                "click .action-save": "save"
            },

            save: function(event) {
                event.preventDefault();
                var that = this;
                this.editorView.save(function(response) {
                    that.hide();
                    that.editorView.problem = response;
                    that.component.find(".problem-content").html(response.content_html);
                });
            },

            options: $.extend({}, BaseModal.prototype.options, {
                modalName: "edit-problem",
                addSaveButton: true,
                "title": "Editing: Problem"
            }),

            initialize: function() {
                BaseModal.prototype.initialize.call(this);
                this.problemEditorTemplate = _.template($("#problem-editor-tpl").html());
                this.events = _.extend({}, BaseModal.prototype.events, this.events);
            },

            edit: function(problem_id) {
                var problem_url = problem_url = "http://192.168.3.10:8000/labster/api/v2/problems/" + problem_id + "/";
                var that = this;
                $.ajax({
                    url: problem_url,
                    type: "GET",
                    success: function(response) {
                        that.show();
                        that.editorView = new LabsterProblemEditorView({
                            el: that.$(".xblock-editor")
                        });
                        that.editorView.problem_url = problem_url;
                        that.editorView.problem = response;
                        that.editorView.render();
                    }

                });
            },

            hide: function() {
                BaseModal.prototype.hide.call(this);

                this.undelegateEvents();
                this.$el.html("");
            },

            getContentHtml: function() {
                return this.problemEditorTemplate();
            },

            something: function() {
            }
        });

        return EditProblemModal;
    }
);

