$(function() {
    $(".invite-students").click(function(event) {
        $("#invite-students-course-name").text($(event.target).data("course-name"));
        $("#invite-students-course-location").val($(event.target).data("course-location"));

        $("#invite-students-form").show();
        $("#invite-students-modal-title").show();
        $("#invite-students-complete").hide();
        $("#invite-students-complete-title").hide();
    });

    $("#invite-students-form").submit(function(event) {
        var el = $(event.currentTarget);
        el.find("input[type=email]").val("");

        $("#invite-students-form").hide();
        $("#invite-students-modal-title").hide();
        $("#invite-students-complete").show();
        $("#invite-students-complete-title").show();
        return false;
    });
});

