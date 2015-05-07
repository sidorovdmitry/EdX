function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", window.csrfToken);
        }
    }
});

function registerModalInit(options) {
    // options:
    // - nextUrl
    // - courseId,
    // - labster_demo

    var createUrl,
        updateUrl,
        loginUrl,
        loginFormUrl,
        containerFormLogin,
        containerFormZero,
        containerFormOne,
        containerFormTwoT,
        containerFormTwoS,
        containerFormThree,
        buttonInSaving,
        resetButton,
        validateForm,
        showFormErrors,
        isDemoCourse;

    isDemoCourse = false
    if (options.isDemoCourse == "True") {
      isDemoCourse = true;
    }

    $('.new-register').click(function(ev) {
        window.userType = $(this).data('user-type');
    });

    createUrl = "/labster/api/users/";
    loginUrl = "/labster/login-by-token/";
    loginFormUrl = "/login_ajax";
    updateUrl = function(userId) {
        return createUrl + userId + "/";
    };
    sendEmailUrl = function(userId) {
        return createUrl + "send-email/" + userId + "/";
    }

    containerFormLogin = $('.login-wizard');
    containerFormZero = $('.register-wizard-0');
    containerFormOne = $('.register-wizard-1');
    containerFormTwoT = $('.register-wizard-2-t');
    containerFormTwoS = $('.register-wizard-2-s');
    containerFormThree = $('.register-wizard-3');

    $('.button-link-submit').click(function(ev) {
        ev.preventDefault();
        $(this).closest('form').submit();
    });

    $('.show-register-form').click(function(){
        containerFormLogin.fadeOut(function(){
          containerFormZero.fadeIn();
        });
    });

    $('.show-login-form').click(function(){
        showLoginForm();
    });

    showLoginForm = function(){
        // when user enters existing email it will show error message 'the email is used'
        // because the message is a new element so it won't trigger $('.show-login-form').click
        containerFormZero.fadeOut(function(){
          containerFormLogin.fadeIn();
        });
    }

    sendEmailTeacher = function() {
      $.ajax({
          url: sendEmailUrl(window.user.id),
          type: "GET",
          beforeSend: function(xhr, settings) {
              xhr.setRequestHeader("Authorization", "Token " + window.user.token_key);
          },
          success: function(response) {
          },
          error: function(obj, msg, status) {
          }
      });
    }

    buttonInSaving = function(button) {
        button.data('original-html', button.html());
        button.html('<i class="icon fa fa-spinner fa-spin"></i> Saving');
    };

    buttonInLoggingIn = function(button) {
        button.data('original-html', button.html());
        button.html('<i class="icon fa fa-spinner fa-spin"></i> Logging in');
    };

    resetButton = function(button) {
        button.html(button.data('original-html'));
    };

    validateForm = function(form) {
      var inputs,
          valid = true;

      form.find('.error-message').empty().hide();
      inputs = form.find('input.required,select.required');
      _.each(inputs, function(input) {
          var el = $(input);

          if (el.val().length == 0) {
              var errorMessage;
              if (input.tagName.toLowerCase() === 'select') {
                  errorMessage = el.closest('.select-container').siblings('.error-message');
              } else {
                  errorMessage = el.next('.error-message');
              }

              errorMessage.show().html('This field is required');
              valid = false;
          }
      });

      return valid;
    };

    showFormErrors = function(form, messages) {
        var getName,
            inputs;

        getName = function(name) {
            return "[name=" + name + "]";
        };

        _.each(messages, function(messageList, name) {
            inputs = form.find(getName(name));
            _.each(inputs, function(input) {
                _.each(messageList, function(message) {
                    if (message == "Email is used") {
                        message = 'Email is already in use. Please <a class="show-login-form" onclick="showLoginForm()">login here</a>.';
                    }
                    $(input).next('.error-message').append(message).show();
                });
            });
        });
    };

    containerFormLogin.find('form').submit(function(ev) {
        var inputEmail,
            submit,
            remember,
            password,
            errorMessage,
            form;

        form = containerFormLogin.find('form');
        inputEmail = form.find('input[name=email]');
        password = form.find('input[name=password]');
        remember = form.find('input[name=remember]');
        submit = form.find('button[type=submit]');
        errorMessage = form.find('.error-message');

        var rememberVal = "";
        if (remember[0].checked) {
            rememberVal = "true";
        }

        buttonInLoggingIn(submit);
        errorMessage.hide().empty();

        if (validateForm(form)) {
            var next = options.nextUrl;
            $.ajax({
                url: loginFormUrl,
                type: "POST",
                data: {email: inputEmail.val(), password:password.val(), remember: rememberVal, course_id: options.courseId},
                success: function(response) {
                    if (response.success) {
                        if (options.courseId != "") {
                            next = "/courses/" + options.courseId + "/courseware";
                        }
                        window.location.href = next;
                    } else {
                        var messages = {
                            email: [response.value]
                        };
                        showFormErrors(form, messages);
                        resetButton(submit);
                    }
                },
                error: function(obj, msg, status) {
                    var response = JSON.parse(obj.responseText);
                    showFormErrors(form, response);
                    resetButton(submit);
                }
            });
        } else {
            resetButton(submit);
        }

    return false;
    });

    containerFormZero.find('form').submit(function(ev) {
        var inputEmail,
            submit,
            email,
            erroMessage,
            form;

        form = containerFormZero.find('form');
        inputEmail = form.find('input[name=email]');
        submit = form.find('button[type=submit]');
        errorMessage = form.find('.error-message');

        email = inputEmail.val();

        buttonInSaving(submit);
        errorMessage.hide().empty();

        if (validateForm(form)) {
            var next = options.nextUrl;
            if (parseInt(window.userType) === 1 && options.courseId != "") {
                if (isDemoCourse) {
                    // if student and it's coming from the about page, redirect to payment page
                    next = "/student_license/" + options.courseId;
                } else {
                    // if it's not demo course
                    next = "/courses/" + options.courseId + "/courseware";
                }
            }

            $.ajax({
                url: createUrl,
                type: "POST",
                data: {email: email, user_type: window.userType},
                success: function(response) {
                    window.user = response;
                    containerFormZero.fadeOut(function() {
                        containerFormOne.fadeIn();
                        containerFormThree.find('input[name=user_id]').val(window.user.id);
                        containerFormThree.find('input[name=user_type]').val(window.userType);
                        containerFormThree.find('input[name=token_key]').val(window.user.token_key);
                        containerFormThree.find('input[name=next]').val(next);
                        containerFormThree.find('input[name=course_id]').val(options.courseId);
                        containerFormThree.find('input[name=is_demo_course]').val(isDemoCourse.toString());
                    });

                },
                error: function(obj, msg, status) {
                    var response = JSON.parse(obj.responseText);
                    showFormErrors(form, response);
                    resetButton(submit);
                }
            });
        } else {
            resetButton(submit);
        }

    return false;
    });

    containerFormOne.find('form').submit(function(ev) {
          var inputName,
              inputPassword,
              submit,
              name,
              password,
              form;

          form = containerFormOne.find('form');
          inputName = form.find('input[name=name]');
          inputPassword = form.find('input[name=password]');
          submit = form.find('button[type=submit]');

          name = inputName.val();
          password = inputPassword.val();

          buttonInSaving(submit);
          errorMessage.hide().empty();

          if (validateForm(form)) {
              $.ajax({
                  url: updateUrl(window.user.id),
                  type: "PUT",
                  data: {name: name, password: password, user_type: window.userType},
                  beforeSend: function(xhr, settings) {
                      xhr.setRequestHeader("Authorization", "Token " + window.user.token_key);
                  },
                  success: function(response) {
                      containerFormOne.fadeOut(function() {
                          if (parseInt(window.userType) === 2) {
                              containerFormTwoT.fadeIn();
                          } else {
                              containerFormTwoS.fadeIn();
                          }
                      });
                  },
                  error: function(obj, msg, status) {
                      resetButton(submit);
                  }
              });
          } else {
              resetButton(submit);
          }

          return false;
    });

    containerFormTwoT.find('form').submit(function(ev) {
          var inputUserSchoolLevel,
              inputOrganizationName,
              inputPhoneNumber,
              submit,
              userSchoolLevel,
              organizationName,
              phoneNumber,
              form,
              payload;

          form = containerFormTwoT.find('form');
          inputUserSchoolLevel = form.find('select[name=user_school_level]');
          inputOrganizationName = form.find('input[name=organization_name]');
          inputPhoneNumber = form.find('input[name=phone_number]');
          submit = form.find('button[type=submit]');

          userSchoolLevel = inputUserSchoolLevel.val();
          organizationName = inputOrganizationName.val();
          phoneNumber = inputPhoneNumber.val();

          buttonInSaving(submit);
          errorMessage.hide().empty();

          payload = {
              user_school_level: userSchoolLevel,
              organization_name: organizationName,
              phone_number: phoneNumber
          };

          if (validateForm(form)) {
              $.ajax({
                  url: updateUrl(window.user.id),
                  type: "PUT",
                  data: payload,
                  beforeSend: function(xhr, settings) {
                      xhr.setRequestHeader("Authorization", "Token " + window.user.token_key);
                  },
                  success: function(response) {
                      containerFormTwoT.fadeOut(function() {
                          containerFormThree.find('form').submit();
                      });
                      // Send email to sales people
                      sendEmailTeacher();
                  },
                  error: function(obj, msg, status) {
                      resetButton(submit);
                  }
              });
          } else {
              resetButton(submit);
          }

          return false;
    });

    containerFormTwoS.find('form').submit(function(ev) {
        var inputLevelOfEducation,
            inputGender,
            inputYearOfBirth,
            submit,
            levelOfEducation,
            gender,
            yearOfBirth,
            form,
            payload;

        form = containerFormTwoS.find('form');
        inputLevelOfEducation = form.find('select[name=level_of_education]');
        inputGender = form.find('select[name=gender]');
        inputYearOfBirth = form.find('select[name=year_of_birth]');
        submit = form.find('button[type=submit]');

        levelOfEducation = inputLevelOfEducation.val();
        gender = inputGender.val();
        yearOfBirth = inputYearOfBirth.val();

        buttonInSaving(submit);
        errorMessage.hide().empty();

        payload = {
            level_of_education: levelOfEducation,
            gender: gender,
            year_of_birth: yearOfBirth
        };

        if (validateForm(form)) {
            $.ajax({
                url: updateUrl(window.user.id),
                type: "PUT",
                data: payload,
                beforeSend: function(xhr, settings) {
                    xhr.setRequestHeader("Authorization", "Token " + window.user.token_key);
                },
                success: function(response) {
                    containerFormTwoS.fadeOut(function() {
                        containerFormThree.find('form').submit();
                    });
                },
                error: function(obj, msg, status) {
                    resetButton(submit);
                }
            });
        } else {
            resetButton(submit);
        }

        return false;
    });

}
