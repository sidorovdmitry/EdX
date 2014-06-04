define(["underscore", "jquery", "js/views/baseview", "js/views/modals/labster_edit_problem"],
    function(_, $, BaseView, EditProblemModal) {
        var QuizBlockDetail = BaseView.extend({
            events: {
                "click .component-actions .edit-button": "clickEditButton"
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
