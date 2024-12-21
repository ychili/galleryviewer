"""Test galleryviewer's command-line interface."""

import subprocess

import pytest

import galleryviewer.main

_EXE = "galleryviewer"
_TEST_PATHS = ["1.jpg", "10.jpg", "2.jpg"]


@pytest.fixture(autouse=True)
def patch_config_paths(monkeypatch):
    """Patch generate_config_paths to return an empty iterator."""
    monkeypatch.setattr(galleryviewer.main, "generate_config_paths", lambda: iter(()))


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
    returncode = galleryviewer.main.main(
        ["--no-test", "--profile", profile_arg, *_TEST_PATHS]
    )
    assert returncode == 0


def test_output(capsys):
    title = "My Awesome Gallery"
    returncode = galleryviewer.main.main(
        ["--no-test", "--profile", "builtin", "--title", title, *_TEST_PATHS]
    )
    assert returncode == 0
    output = capsys.readouterr().out
    assert all(word in output for word in ["</html>", title, "pageIndex", "#content"])
