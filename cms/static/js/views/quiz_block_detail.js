define(["underscore", "jquery", "js/views/baseview", "js/views/modals/labster_edit_problem",
        "js/views/modals/labster_create_problem", "js/views/feedback_notification",
        "js/views/feedback_prompt"],
    function(_, $, BaseView, EditProblemModal, CreateProblemModal, NotificationView, PromptView) {
        var QuizBlockDetail = BaseView.extend({
            events: {
                "click .nav-actions .new-problem-button": "clickNewButton",
                "click .component-actions .edit-button": "clickEditButton",
                "click .component-actions .delete-button": "clickDeleteButton"
            },

            clickNewButton: function(event) {
                event.preventDefault();
                var el = $(event.currentTarget);
                var url = el.data("url");
                var quiz_block_id = el.data("quiz-block-id");

                var modal = new CreateProblemModal();
                modal.quiz_block_id = quiz_block_id;
                modal.create();
            },

            clickEditButton: function(event) {
                event.preventDefault();
                var el = $(event.currentTarget);
                var component_el = el.closest(".component");
                var problem_id = el.data("problem-id");

                var modal = new EditProblemModal();
                modal.component = component_el;
                modal.edit(problem_id);
            },

            clickDeleteButton: function(event) {
                event.preventDefault();
                var el = $(event.currentTarget);
                var problem_id = el.data('problem-id');
                var msg = new PromptView.Warning({
                    title: gettext('Delete this problem?'),
                    message: gettext('Deleting this problem is permanent and cannot be undone.'),
                    actions: {
                        primary: {
                            text: gettext('Yes, delete this problem'),
                            click: function(view) {
                                view.hide();

                                var component_el = el.closest('.component');
                                var deleting = new NotificationView.Mini({
                                    title: gettext('Deleting&hellip;')
                                });
                                deleting.show();
                                var problem_url = "http://localhost:8000/labster/api/v2/problems/" + problem_id + "/";
                                $.ajax({
                                    type: "DELETE",
                                    url: problem_url,
                                }).success(function() {
                                    component_el.remove();
                                    deleting.hide();
                                });

                            }
                        },
                        secondary: {
                            text: gettext('Cancel'),
                            click: function(view) {
                                return view.hide();
                            }
                        }
                    }
                });
                return msg.show();

            }

        });

        return QuizBlockDetail
    }
)
