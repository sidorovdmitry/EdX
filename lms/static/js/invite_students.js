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

        var duplicate_course = function() {
            var course_location = $("#invite-students-course-location").val();
            var url = '//' + window.cms_base + '/labster/api/course/duplicate/';
            var data = {
                source: course_location
            };

            postJSON(url, data, invite_students);
        };

        var invite_students = function(response) {
            $("#invite-students-complete").prop("action", "/courses/" + response.course_id + "/instructor#view-membership");

            var emails = [];
            $.each(el.find('input[type=email]'), function(index, input) {
                var input_el = $(input);
                if (input_el.val()) {
                    emails.push(input_el.val());
                }
            });

            var url = "/courses/" + response.course_id + "/instructor/api/students_update_enrollment";
            var data = {
                action: "enroll",
                auto_enroll: true,
                email_students: true,
                identifiers: emails.join(",")
            }

            $.post(url, data, function(response) {
                show_success();
            });
        };

        var show_success = function(response) {
            el.find("input[type=email]").val("");

            $("#invite-students-run").hide();
            $("#invite-students-run-title").hide();

            $("#invite-students-complete").show();
            $("#invite-students-complete-title").show();
        }

        duplicate_course();
        return false;
    });
});

