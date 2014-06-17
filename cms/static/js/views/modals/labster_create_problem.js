define(["underscore", "jquery", "js/views/modals/base_modal", "js/views/labster_problem_editor"],
    function(_, $, BaseModal, LabsterProblemEditorView) {
        var CreateProblemModal = BaseModal.extend({
            events: {
                "click .action-save": "save"
            },

            save: function(event) {
                event.preventDefault();
                var that = this;
                this.editorView.save("POST", function(response) {
                    that.hide();
                    // that.editorView.problem = response;
                    // that.component.find(".problem-content").html(response.content_html);
                });
            },

            options: $.extend({}, BaseModal.prototype.options, {
                modalName: "create-problem",
                addSaveButton: true,
                "title": "Create: Problem"
            }),

            initialize: function() {
                BaseModal.prototype.initialize.call(this);
                this.problemEditorTemplate = _.template($("#problem-editor-tpl").html());
                this.events = _.extend({}, BaseModal.prototype.events, this.events);
            },

            create: function() {
                var problem_url = "http://localhost:8000/labster/api/v2/problems/";

                this.show();
                this.editorView = new LabsterProblemEditorView({
                    el: this.$(".xblock-editor")
                });

                this.editorView.problem_url = problem_url;
                this.editorView.problem = {quiz_block: this.quiz_block_id};
                this.editorView.render();
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

        return CreateProblemModal;
    }
);

