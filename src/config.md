see the description on https://ankiweb.net/shared/info/319501851.

For shortcuts in the pdf viewer see: https://github.com/mozilla/pdf.js/wiki/Frequently-Asked-Questions#what-are-the-pdfjs-keyboard-shortcuts

This add-on includes a hack so that in pdfjs the colors of the pdf and the surrounding toolbar can be inverted (night mode). This has multiple flaws but I still use it because I really dislike looking at a bright white pdf at night. You can disable it by setting  `"apply night mode hacks to invert colors by default"` to `false`.

The underlying toolkit that Anki uses bundles a pdf viewer since around Anki 2.1.35 (well after the first version of my add-on was released). The problem with this bundled pdf viewer is that - unless you are on the latest anki builds with pyqt6 - a pdf is always opened on page 1. In this viewer there's also no night mode support. It's faster though. If you want to use it change the setting `"use pdfjs to show pdfs in Anki 2.1.50+ (with pyqt6)"` to `false`.

&nbsp;
&nbsp;
&nbsp;
&nbsp;
&nbsp;
&nbsp;

#### Credits
This add-on was made by ijgnd. I use some code made by other people:Copyright<br>
(c) 2019- ijgnd<br>
License: GNU AGPLv3, https://www.gnu.org/licenses/agpl.html

&nbsp;

This add-on bundles pdfjs (license Apache Licens Version 2.0, January 2004).
For the licence text file: see the addon-folder, subfolder "web". It's in each
pdfjs folder.

&nbsp;

The source code for the filter dialog is in the file fuzzy_panel.py. Most of
the code inside this file was originally made by Rene Schallner for his 
https://github.com/renerocksai/sublimeless_zk. I made some changes to these files. 
For details see the top of this file. This file is licensed as GNU GPLv3, 
https://www.gnu.org/licenses/gpl.html. The license is in the add-on folder, subfolder
"copied".

&nbsp;
&nbsp;

This add-on uses the file icons/folder-plus_mod.svg. This is a slight modification 
("black" instead of "currentColor") of the file 
https://raw.githubusercontent.com/feathericons/feather/master/icons/folder-plus.svg 
which is covered by the following copyright and permission notice,
https://github.com/feathericons/feather/blob/master/LICENSE:

The MIT License (MIT)

Copyright (c) 2013-2017 Cole Bemis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

&nbsp;
&nbsp;

This add-on bundles the file "js_base64_minified_for_pdf_viewer_addon.js". This file was generated
from https://raw.githubusercontent.com/dankogai/js-base64/main/base64.js with the package terser
with the command "terser -m -c" in 2022-07-15. js-base64 has this copyright and permission notice:

Copyright (c) 2014, Dan Kogai All rights reserved.

Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:

Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.

Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.

Neither the name of {{{project}}} nor the names of its contributors may be used to endorse or promote products derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
