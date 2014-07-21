from xblock.fields import Scope, String
from xmodule.x_module import XModule, XModuleDescriptor


class QuizblockFields(object):

    quizblock_id = String(
        display_name="Quizblock ID",
        help="Quizblock ID.",
        scope=Scope.settings,
        # it'd be nice to have a useful default but it screws up other things; so,
        # use display_name_with_default for those
        default=None
    )

    description = String(
        display_name="Description",
        help="Description.",
        scope=Scope.settings,
        # it'd be nice to have a useful default but it screws up other things; so,
        # use display_name_with_default for those
        default=None
    )


class QuizblockModule(QuizblockFields, XModule):

    def get_html(self):
        context = {
            'description': self.description,
        }
        return self.system.render_template('quizblock.html', context)


class QuizblockDescriptor(QuizblockFields, XModuleDescriptor):
    module_class = QuizblockModule

    def get_html(self):
        context = {}
        return self.system.render_template('quizblock.html', context)
