"""Test galleryviewer's command-line interface."""

import pathlib
import subprocess

import pytest

import galleryviewer.main

_EXE = "galleryviewer"
_TEST_PATHS = ["1.jpg", "10.jpg", "2.jpg"]


@pytest.fixture(autouse=True)
def patch_config_paths(monkeypatch):
    """Patch generate_config_paths to return an empty iterator."""
    monkeypatch.setattr(galleryviewer.main, "generate_config_paths", lambda: iter(()))


def _check_output(output, title=""):
    return all(word in output for word in ["</html>", title, "pageIndex", "#content"])


def _main_no_test(options=None):
    options = options or []
    argv = ["--no-test", *options, *_TEST_PATHS]
    return galleryviewer.main.main(argv)


def test_version():
    subprocess.run([_EXE, "--version"], check=True)


def test_help():
    subprocess.run([_EXE, "--help"], check=True)


@pytest.mark.parametrize(
    "sort_arg, expected",
    [
        ("none", _TEST_PATHS),
        ("ascii", _TEST_PATHS),
        ("human", ["1.jpg", "2.jpg", "10.jpg"]),
    ],
)
def test_check_sort_output(capsys, sort_arg, expected):
    returncode = galleryviewer.main.main(
        ["--check-sort", *_TEST_PATHS, f"--sort={sort_arg}"]
    )
    assert returncode == 0
    result = capsys.readouterr().out.splitlines()
    assert result == expected, (result, expected)


@pytest.mark.parametrize(
    "profile_arg", ["builtin", "builtin/default.html", "builtin/dark.html"]
)
def test_builtin_profiles(profile_arg):
    returncode = _main_no_test(options=["--profile", profile_arg])
    assert returncode == 0


def test_output(capsys):
    title = "My Awesome Gallery"
    returncode = _main_no_test(options=["--profile", "builtin", "--title", title])
    assert returncode == 0
    output = capsys.readouterr().out
    assert _check_output(output, title=title)


def test_fatal_errors_data_file_path(tmp_path):
    data_file_path = tmp_path / "error_file.json"
    options = ["--data-file", str(data_file_path)]
    returncode = _main_no_test(options=options)
    assert returncode == 1
    data_file_path.write_bytes(b"{")
    returncode = _main_no_test(options=options)
    assert returncode == 100


def test_fatal_errors_template_file_path(tmp_path):
    template_file_path = tmp_path / "error_file.jinja2"
    returncode = _main_no_test(options=["--template", str(template_file_path)])
    assert returncode == 1


def test_fatal_errors_unknown_profile_name():
    returncode = _main_no_test(options=["--profile", "builtin/nonexistent"])
    assert returncode == 101


def test_file_output_option(tmp_path):
    output_file_path = tmp_path / "output.html"
    returncode = _main_no_test(options=["--output", str(output_file_path)])
    assert returncode == 0
    assert _check_output(output_file_path.read_text(), title=pathlib.Path.cwd().name)
