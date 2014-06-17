define(["underscore", "jquery", "js/views/baseview", "js/views/modals/labster_edit_problem", "js/views/modals/labster_create_problem"],
    function(_, $, BaseView, EditProblemModal, CreateProblemModal) {
        var QuizBlockDetail = BaseView.extend({
            events: {
                "click .nav-actions .new-problem-button": "clickNewButton",
                "click .component-actions .edit-button": "clickEditButton"
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
            }
        });

        return QuizBlockDetail
    }
)
