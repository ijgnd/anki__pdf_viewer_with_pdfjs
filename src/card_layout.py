from pprint import pprint as pp  # noqa

from anki.hooks import wrap
from aqt.clayout import CardLayout
from aqt.utils import showInfo
from aqt.qt import *

from .config import gc, pointversion
if pointversion < 28:
    from .forms import addtofield  # noqa
else:
    from .forms import addtofield28 as addtofield  # noqa


def my_setup_buttons(self):
    on_ext_docs_but = QPushButton("Ext-Docs-Link")
    on_ext_docs_but.setAutoDefault(False)
    self.buttons.insertWidget(3, on_ext_docs_but)
    on_ext_docs_but.clicked.connect(self.on_ext_docs_link)
    tm = ("This button belongs to the add-on 'anki pdf viewer (pdfjs)'."
          "For more info go to https://ankiweb.net/shared/info/319501851")
    on_ext_docs_but.setToolTip(tm)
CardLayout.setupButtons = wrap(CardLayout.setupButtons, my_setup_buttons)  # noqa


def on_ext_docs_link(self):
    filefield = gc("field_for_filename", "external_source")
    pagefield = gc("field_for_page", "external_page")
    fieldnames = [f['name'] for f in self.model['flds']]
    if filefield not in fieldnames or pagefield not in fieldnames:
        msg = ("Your setup for the Add-on 'anki pdf viewer (pdfjs)' "
               "is not valid.\n\n"
               "Your notetype doesn't contain fields with the names %s and %s"
               "which you set in the config of this add-on. Either use one of the note"
               "types bundled with this add-on or add fields with these names to this note type.\n\n"
               "If you don't know what I mean by 'add fields to your note type' watch"
               "this video https://www.youtube.com/watch?v=JTKqd4nqsK0&feature=youtu.be&t=22" % (
                   filefield, pagefield
               ))
        showInfo(msg)
        return
    diag = QDialog(self)
    form = addtofield.Ui_Dialog()
    form.setupUi(diag)
    form.linktext.setText("View external file: {{text:%s}}" % filefield)
    form.font.setCurrentFont(QFont("Arial"))
    form.size.setValue(20)
    diag.show()
    if not diag.exec():
        return
    if pointversion < 28:
        if form.radioQ.isChecked():
            obj = self.tform.front
        else:
            obj = self.tform.back
    else:
        obj = self.tform.edit_area
    t = obj.toPlainText()
    t += ("""\n<a href='javascript:pycmd("pdfjs319501851"""
          """{{text:%s}}319501851{{text:%s}}");'"""
          """>%s</a>""" % (filefield, pagefield, form.linktext.text()))
    obj.setPlainText(t)
    if pointversion < 28:
        self.saveCard()
CardLayout.on_ext_docs_link = on_ext_docs_link  # noqa
