see the description on https://ankiweb.net/shared/info/319501851.

If the pdf file is not shown you might want to use the pdfjs version that was bundled 
as the default between 2021-05 and 2022-07. To do this change the setting 
`"pdf_js_version_used"` to `"mid_2021"`.

This add-on includes a hack so that in pdfjs the colors of the pdf and the 
surrounding toolbar can be inverted (night mode). This has multiple flaws
but I still use it because I really dislike looking at a bright white pdf
at night. You can enable it by setting 
`"apply night mode hacks to invert colors by default"` to `true`.

The underlying toolkit that Anki uses bundles a pdf viewer since around
Anki 2.1.35 (well after the first version of my add-on was released). The 
problem with this bundled pdf viewer is that - unless you are on the 
latest anki builds with pyqt6 - a pdf is always opened on page 1. So 
I only default to this built-in viewer if you use on Anki 2.1.50 with pyqt6. 
If you still want to use pdfjs in these new versions change the setting 
`"use pdfjs to show pdfs in Anki 2.1.50+ (with pyqt6)"` to `false`.
