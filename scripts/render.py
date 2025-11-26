"""Script to insert metadata in man page.

Usage: render.py package_source [source_timestamps...] < input > output
"""

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
    timestamps = sys.argv[2:]
    if timestamps:
        # Use the latest source timestamp.
        struct_time = time.gmtime(max(int(timestamp) for timestamp in timestamps))
    else:
        # Use current time.
        struct_time = time.gmtime()
    data["date"] = time.strftime("%Y-%m-%d", struct_time)
    template = jinja2.Template(sys.stdin.read())
    sys.stdout.write(template.render(data))


if __name__ == "__main__":
    try:
        main()
    except Exception:
        print(__doc__, file=sys.stderr)
        raise
