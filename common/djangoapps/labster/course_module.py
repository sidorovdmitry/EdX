from xblock.fields import Scope, List, String, Dict, Boolean, Integer, Float

_ = lambda text: text


class LabsterCourseFields(object):

    is_browsable = Boolean(
        display_name=_("Course is Displayed in Front Page"),
        help=_("Enter true or false. If true, the course is displayed. If false, the course is hidden."),
        scope=Scope.settings,
        default=False,
    )
    show_course_info = Boolean(
        display_name=_("Course Info is Shown"),
        help=_("Enter true or false. If true, the course is displayed. If false, the course info is hidden."),
        scope=Scope.settings,
        default=True,
    )
    main_wiki_page = String(
        display_name=_("Main Wiki Page for the Course"),
        help=_("Enter the page for the main page. If empty, it'll use default /wiki/course.id/"),
        scope=Scope.settings,
        default="",
    )
    labster_demo = Boolean(
        display_name=_("Labster Demo Course"),
        help=_("Enter true or false. If true, it will have all demo features."),
        scope=Scope.settings,
        default=False,
    )
    labster_license = Boolean(
        display_name=_("Labster License Course"),
        help=_("Enter true or false. If true, it will validate the student register."),
        scope=Scope.settings,
        default=False,
    )
    labster_verified = Boolean(
        display_name=_("Labster Verified Lab"),
        help=_("Enter true or false. If true, it will check for user's verified status before showing the lab."),
        scope=Scope.settings,
        default=False,
    )
    labtser_language = String(
        display_name=_("Labster Lab Language"),
        help=_("Enter the language code for the Lab. The default is en."),
        scope=Scope.settings,
        default="en",
    )
