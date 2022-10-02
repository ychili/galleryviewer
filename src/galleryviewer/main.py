import argparse
import configparser
import json
import logging
import os
import pathlib
import re
import sys
from dataclasses import dataclass

from jinja2 import (Environment, FileSystemLoader, PackageLoader, PrefixLoader,
                    TemplateNotFound, select_autoescape)

from . import _PROG, __version__

DEFAULT_TMPL_NAME = "default.html"
OPTION_DEFAULTS = {"data_file": None,
                   "ignore_case": True,
                   "profile": f"builtin/{DEFAULT_TMPL_NAME}",
                   "sort": "human",
                   "test": False}


@dataclass
class ImagePath:
    arg: str
    index: int

    @property
    def path(self):
        return pathlib.Path(self.arg)


class Config:

    def __init__(self, parser=None, rules=None):
        self.parser = parser or configparser.ConfigParser(os.environ)
        self.rules = rules or {}
        self.profiles = {}
        self.options = {}

    @staticmethod
    def parse_profiles(mapping):
        """Return new mapping with path values expanded."""
        return {key: os.path.expanduser(value)
                for key, value in mapping.items()}

    @staticmethod
    def parse_options(mapping, rules, source=None):
        """Return new mapping of options parsed by *rules* from *mapping*."""
        source = source or "<???>"
        parsed = {}
        for opt in mapping:
            opt_rule = rules.get(opt)
            if opt_rule is None:
                continue
            value = opt_rule.get(mapping, opt)
            if value is None:
                # value was rejected by a rule
                logging.warning(
                    "in %r: invalid value for config option %s: %s",
                    source, opt, mapping[opt])
                continue
            parsed[opt_rule.dest] = value
        return parsed

    def read_file(self, file, source=None):
        """Read and parse a file-like object.

        If reading the file generates configparser errors, then emit a warning
        and return without updating self.
        """
        source = source or getattr(file, "name", None) or "<???>"
        try:
            self.parser.read_file(file, source=source)
        except configparser.Error as err:
            logging.warning("in %r: %s", source, err)
            return
        if "options" in self.parser:
            self.options.update(
                self.parse_options(self.parser["options"], self.rules, source))
        if "profiles" in self.parser:
            self.profiles.update(
                self.parse_profiles(self.parser["profiles"]))

    def read(self, filenames, encoding="utf-8"):
        """Read and parse an iterable of filenames.

        Files that cannot be opened are silently ignored.

        Return list of successfully read files.
        """
        found = []
        for filename in filenames:
            try:
                file = open(filename, "r", encoding=encoding)
            except OSError:
                continue
            with file:
                self.read_file(file, source=filename)
            found.append(filename)
        return found


class StoreRule:

    def __init__(self, dest, converter=""):
        self.dest = dest
        self.converter = f"get{converter}"

    def get(self, mapping, option):
        """Convert the value, and return it."""
        return getattr(mapping, self.converter)(option)

    def __repr__(self):
        attrs = [f"{attr}={val!r}" for attr, val in vars(self).items()]
        return f"{type(self).__name__}({', '.join(attrs)})"


class ChoicesRule(StoreRule):

    def __init__(self, dest, choices, converter=""):
        super().__init__(dest, converter)
        self.choices = choices

    def get(self, mapping, option):
        """
        Convert the value, return None if not in *choices*, otherwise return
        the value.
        """
        value = getattr(mapping, self.converter)(option)
        if value in self.choices:
            return value
        return None


class ActionsRule(StoreRule):

    def __init__(self, dest, actions, converter=""):
        super().__init__(dest, converter)
        self.actions = actions

    def get(self, mapping, option):
        """
        Convert the value, return None if not in *actions*, otherwise return
        the mapped value from *actions*.
        """
        value = getattr(mapping, self.converter)(option)
        return self.actions.get(value)


def rule(dest, converter="", choices=None, actions=None):
    """Return an option parsing rule."""
    if choices is not None:
        return ChoicesRule(dest=dest, converter=converter, choices=choices)
    if actions is not None:
        return ActionsRule(dest=dest, converter=converter, actions=actions)
    return StoreRule(dest=dest, converter=converter)


def atoi(string):
    """Also known as try_int"""
    try:
        return int(string)
    except ValueError:
        return string


def alphanum_key(string):
    """Turn a string into a list of string and number chunks.

    >>> alphanum_key("z23a")
    ['z', 23, 'a']
    """
    return [atoi(char) for char in re.split("([0-9]+)", string)]


def main():
    logging.basicConfig(level=logging.INFO,
                        format=f"{_PROG}: %(levelname)s: %(message)s")
    config = get_config()
    args = parse_cla(config.options)

    files = create_paths(args.paths, args.sort, args.ignore_case)
    if args.check_sort:
        check_sort(files, args.sort)
        return 0
    if args.test:
        if not test_paths(files):
            return 1

    try:
        data = load_data_file(file=args.data_file)
    except json.JSONDecodeError as err:
        logging.error("unable to decode %s as JSON: %s", args.data_file, err)
        return 100

    env = get_environment(config.profiles.items())
    try:
        template = load_template(env, name=args.profile, file=args.template)
    except TemplateNotFound as err:
        logging.error("template not found: %s", err.message)
        return 101

    substitutions = {
        "title": args.title or pathlib.Path.cwd().name,
        "files": files,
        "data": data
    }
    emit(args.output, template, substitutions)
    return 0


def get_config():
    parser = configparser.ConfigParser(
        interpolation=None)
    data_file_rule = rule(dest="data_file")
    rules = {
        "sort": rule(dest="sort", choices=(
            "none", "ascii", "human", "default")),
        "case": rule(dest="ignore_case", actions={
            "ignore": True, "consider": False}),
        "test": rule(dest="test", converter="boolean"),
        "data-file": data_file_rule,
        "datafile": data_file_rule,
        "profile": rule(dest="profile")
    }
    config = Config(parser, rules)
    config.options = OPTION_DEFAULTS
    config.read(generate_config_paths())
    return config


def create_paths(paths, sort_method=None, caseless=True):
    """Create and return a sorted list of ImagePaths."""
    files = [ImagePath(arg, ind) for ind, arg in enumerate(paths)]
    if sort_method == "none":
        return files
    if sort_method is None or sort_method == "default":
        sort_method = "human"
    str_func = str.casefold if caseless else str
    if sort_method == "ascii":
        key_func = str
    elif sort_method == "human":
        key_func = alphanum_key
    else:
        raise ValueError(sort_method)
    files.sort(key=lambda p: key_func(str_func(p.arg)))
    return files


def check_sort(files, sort_method=None):
    logging.info("chosen sort method: %s", sort_method or "auto")
    for file in files:
        print(file.arg)


def test_paths(files):
    """If not all paths in *files* exist, emit an error and return False."""
    for file in files:
        if not file.path.is_file():
            logging.error(
                "path %s does not exist or is not a regular file", file.path)
            return False
    return True


def load_data_file(file=None):
    if file is not None:
        with file:
            return json.load(file)
    return {}


def generate_config_paths():
    yield f"/etc/{_PROG}.conf"
    xdg_config_home = os.getenv("XDG_CONFIG_HOME")
    home = os.getenv("HOME")
    if xdg_config_home:
        yield os.path.join(xdg_config_home, _PROG, "config")
    elif home:
        yield os.path.join(home, ".config", _PROG, "config")


def add_default_suffix(arg):
    """Convert arg into a prefixed template name."""
    if '/' not in arg:
        # Treat arg as a profile name
        return f"{arg}/{DEFAULT_TMPL_NAME}"
    return arg


def get_environment(prefixes, **env_kwargs):
    mapping = {profile: FileSystemLoader(path)
               for profile, path in prefixes}
    mapping["builtin"] = PackageLoader(_PROG)
    loader = PrefixLoader(mapping)
    return Environment(loader=loader,
                       autoescape=select_autoescape({"html", "htm", "jinja"}),
                       trim_blocks=True,
                       lstrip_blocks=True,
                       keep_trailing_newline=True,
                       **env_kwargs)


def load_template(env, name, file=None):
    if file is not None:
        with file:
            return env.from_string(file.read())
    return env.get_template(name)


def emit(outfile, template, context):
    document = template.render(context)
    if outfile == sys.stdout:
        return outfile.write(document)
    with outfile:
        return outfile.write(document)


def parse_cla(defaults):
    """Parse command-line arguments."""
    # If defaults does not contain all needed argument defaults, raise
    # KeyError. This is just easier to debug than providing another layer of
    # get defaults.
    parser = argparse.ArgumentParser(
        prog=_PROG, description="Create an HTML viewer for images")
    parser.add_argument(
        "paths", nargs="+", metavar="PATHS",
        help="image file paths to include in viewer")
    parser.add_argument(
        "-V", "--version", action="version",
        version=f"%(prog)s {__version__}")
    sorting = parser.add_argument_group("sorting options")
    sorting.add_argument(
        "-n", "--check-sort", action="store_true",
        help="print PATHS in chosen sorting order; don't emit HTML")
    case = sorting.add_mutually_exclusive_group()
    case.add_argument(
        "-c", "--consider-case", action="store_false", dest="ignore_case",
        default=defaults["ignore_case"],
        help="consider letter case when sorting PATHS")
    case.add_argument(
        "-f", "--ignore-case", action="store_true",
        default=defaults["ignore_case"],
        help="casefold PATHS when sorting")
    sort_method = sorting.add_mutually_exclusive_group()
    sort_method.add_argument(
        "--sort", type=str.lower,
        choices=["none", "ascii", "human"], default=defaults["sort"],
        help="sorting method to apply to PATHS: none (-U), ascii or "
             "lexicographic, human or natural order (default)")
    sort_method.add_argument(
        "-U", "--no-sort", action="store_const", const="none", dest="sort",
        help="include PATHS in the order passed without sorting")
    parser.add_argument(
        "-d", "--data-file", metavar="FILE", default=defaults["data_file"],
        type=argparse.FileType("r", encoding="utf-8"),
        help="load data from %(metavar)s in JSON format")
    parser.add_argument(
        "-o", "--output", metavar="FILE", default=sys.stdout,
        type=argparse.FileType("w", encoding="utf-8"),
        help="place output into %(metavar)s (default is stdout)")
    parser.add_argument(
        "-p", "--profile",
        default=defaults["profile"], type=add_default_suffix,
        help="use PROFILE instead of %(default)s")
    parser.add_argument(
        "-t", "--template", metavar="FILE",
        type=argparse.FileType("r"),
        help="load template directly from %(metavar)s")
    testing = parser.add_mutually_exclusive_group()
    testing.add_argument(
        "--test", action="store_true", default=defaults["test"],
        help="exit if not all PATHS exist as files")
    testing.add_argument(
        "--no-test", action="store_false",
        dest="test", default=defaults["test"],
        help="don't test PATHS for existence")
    parser.add_argument(
        "-T", "--title",
        help="custom title (default is current directory name)")
    return parser.parse_args()
