$(function() {
    function postJSON(url, data, callback) {
        $.ajax({type:'POST',
            url: url,
            dataType: 'json',
            data: data,
            beforeSend: function(xhr) {
                xhr.setRequestHeader("Authorization", "Token " + window.user_token_key);
            },
            success: callback,
            headers : {'X-CSRFToken': $.cookie('csrftoken')}
        });
    }

    $(".invite-students").click(function(event) {
        $("#invite-students-course-name").text($(event.target).data("course-name"));
        $("#invite-students-course-location").val($(event.target).data("course-location"));

        $("#invite-students-form").show();
        $("#invite-students-modal-title").show();
        $("#invite-students-complete").hide();
        $("#invite-students-complete-title").hide();
    });

    $("#invite-students-form").submit(function(event) {
        event.preventDefault();
        $("#invite-students-form").hide();
        $("#invite-students-modal-title").hide();

        $("#invite-students-run").show();
        $("#invite-students-run-title").show();

        var el = $(event.currentTarget);

        var course_location = $("#invite-students-course-location").val();
        var url = '//' + window.cms_base + '/labster/api/course/duplicate/';
        console.log(url);
        var data = {
            source: course_location
        };
        postJSON(url, data, function(response) {
            console.log(response);

            el.find("input[type=email]").val("");

            $("#invite-students-run").hide();
            $("#invite-students-run-title").hide();

            $("#invite-students-complete").show();
            $("#invite-students-complete-title").show();

        });
        return false;
    });
});

