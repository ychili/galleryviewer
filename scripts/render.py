"""Substitute variables in template.

Usage: render.py package_source source_documents... < input > output
"""
import os
import sys
import time

import jinja2


def pkg_version(path):
    with open(path, encoding="utf-8") as src_file:
        for line in src_file:
            if line.startswith("__version__"):
                delim = '"' if '"' in line else "'"
                return line.split(delim)[1]
    msg = "Unable to find version string."
    raise RuntimeError(msg)


def main():
    data = {"version": pkg_version(sys.argv[1])}
    doc_sources = sys.argv[2:]
    mtime = max(os.stat(filename).st_mtime for filename in doc_sources)
    data["date"] = time.strftime("%Y-%m-%d", time.gmtime(mtime))
    template = jinja2.Template(sys.stdin.read())
    sys.stdout.write(template.render(data))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(__doc__, file=sys.stderr)
        raise
