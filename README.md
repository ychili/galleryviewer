Galleryviewer
=============

Create an HTML viewer for an ordered gallery of images.

The program will take a series of paths to image files, sort them (by
default), place them within an HTML template, and write the resultant
file (by default to standard output).
The result is an HTML document for browsing and viewing the images.

Requirements
============

-   Python v3.6+
-   Setuptools
-   [Jinja2
    v2.9+](https://palletsprojects.com/p/jinja/ "Jinja2 template engine")

For building the documentation:

-   `make`, `sh`, `gzip`, `stat`
-   [Groff](https://www.gnu.org/software/groff/ "GNU troff (Groff)")

Building
========

Make will place targets in a directory called `data`.
The default Make target will generate the gzipped man pages
with the version number set to the current version number
and the date set to the last doc source modification time in UTC.
`make html` will create HTML versions of these man pages.

After running make, build the Python package
(using Setuptools or a build frontend such as
[build](https://pypi.org/project/build/)).

Usage
=====

    galleryviewer [options] PATHS...

Provide the image filenames as arguments PATHS.
Or, better, from the Unix shell,
provide a glob pattern, like `*.jpg` or `*.png`,
which the shell will then expand into a list of filenames that match that
pattern.
The program outputs the viewer file as text.
Either use the `--output` option or the shell redirection operator, `>`,
to save it to a file such as "index.html".

Consult the docs for details.
Man page **galleryviewer**(1) describes the main function of the program
and command-line arguments.
Man page **galleryviewer.conf**(5) describes the format of the
configuration file used for some additional features, namely setting
default arguments and custom template locations.

Copyright
=========

Copyright 2022-2025 Dylan Maltby

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.
