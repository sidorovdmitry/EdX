from wiki.editors.base import BaseEditor
from wiki.editors.markitup import MarkItUpAdminWidget, MarkItUpWidget


class CustomContent(BaseEditor):
    editor_id = 'customcontent'

    def get_admin_widget(self, instance=None):
        return MarkItUpAdminWidget()

    def get_widget(self, instance=None):
        return MarkItUpWidget()

    class AdminMedia:
        css = {
            'all': ("wiki/markitup/skins/simple/style.css",
                    "wiki/markitup/sets/admin/style.css",)
        }
        js = ("wiki/markitup/admin.init.js",
              "wiki/markitup/jquery.markitup.js",
              "wiki/markitup/sets/admin/set.js",
              )

    class Media:
        css = {
            "wiki/tinymce/labster.css",
        }
        js = (
            "wiki/tinymce/tinymce.min.js",
            "wiki/marked.js",
            "wiki/to-markdown.js",
            "js/wiki/custom_content.js",
        )
