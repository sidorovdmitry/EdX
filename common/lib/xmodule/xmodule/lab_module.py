# For lab

from xblock.fields import Scope, String, Integer
from xblock.fragment import Fragment
from xmodule.vertical_module import VerticalModule, VerticalDescriptor


class LabModule(VerticalModule):

    def student_view(self, context):
        fragment = Fragment()
        contents = []

        for child in self.get_display_items():
            if child.category == 'problem':
                continue

            rendered_child = child.render('student_view', context)
            fragment.add_frag_resources(rendered_child)

            contents.append({
                'id': child.id,
                'content': rendered_child.content
            })

        fragment.add_content(self.system.render_template('vert_module.html', {
            'items': contents
        }))
        return fragment


class LabDescriptor(VerticalDescriptor):
    module_class = LabModule

    lab_id = String(
        display_name="Lab ID",
        help="Lab ID.",
        scope=Scope.settings,
        # it'd be nice to have a useful default but it screws up other things; so,
        # use display_name_with_default for those
        default=None
    )

    has_quizblocks = Integer(
        help="Default quizblocks are created",
        default=0,
        scope=Scope.settings)
