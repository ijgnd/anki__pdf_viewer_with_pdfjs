from aqt import gui_hooks
from aqt.addcards import AddCards
from aqt.browser import Browser
from aqt.editcurrent import EditCurrent
from aqt.editor import Editor

from .config import gc, pycmd_string


# NOTE: I can have all kinds of filenames and extensions after the inline_prefix. So it doesn't
#       make sense to make them clickable?
#       BUT match until next space?
def append_js_to_Editor(web_content, context):
    if not gc("inline_prefix"):
        return
    if not isinstance(context, Editor):
        return    
    script_str = """
<script>
var external_prefix_regex = new RegExp("PREFIX[^\s]+");
window.addEventListener('dblclick', function (e) {
    const st = window.getSelection().toString();
    if (st != ""){
        if (external_prefix_regex.test(st)){
            pycmd("PYCMD_STRING" + st);
        }
    }
});
</script>
""".replace("PREFIX", gc("inline_prefix"))\
   .replace("PYCMD_STRING", pycmd_string)
    web_content.head += script_str
gui_hooks.webview_will_set_content.append(append_js_to_Editor)
