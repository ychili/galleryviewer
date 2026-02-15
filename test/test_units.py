"""Unit test functions in main module."""

# pylint: disable=too-many-arguments,too-many-positional-arguments

import configparser

import pytest

import galleryviewer.main


class TestConfig:
    @pytest.fixture
    def config(self):
        return galleryviewer.main.get_config()

    @pytest.fixture
    def set_options(self, config):
        def _set(options):
            config.parser.read_dict({"options": options})
            config.parse_options(config.parser["options"])
            return config

        return _set

    def test_get_config(self, config):
        assert config.options == galleryviewer.main.OPTION_DEFAULTS
        assert not config.profiles
        assert not config.read([])

    def test_read_errors(self, config, tmp_path, caplog):
        assert not config.read([tmp_path / "no.conf"])
        windows_wtf = tmp_path / "utf16.conf"
        windows_wtf.write_text("[options]\r\n\r\n[profiles]\r\n", encoding="UTF-16LE")
        assert config.read([windows_wtf]) == [windows_wtf]
        # No UnicodeDecodeErrors, but configparser barfs
        assert windows_wtf.name in caplog.text

    def test_parse_options(self, set_options):
        config = set_options({"unknown": "value"})
        assert "unknown" not in config.options, "Unknown options are not added"

    @pytest.mark.parametrize("value", {"none", "ascii", "human", "default"})
    @pytest.mark.parametrize("opt_key", ["sort", "Sort"])
    def test_sort_choices_valid(self, set_options, caplog, opt_key, value):
        config = set_options({opt_key: value})
        print(config.options)
        print(config.rules)
        assert config.options["sort"] == value
        assert not caplog.messages

    def test_sort_choices_invalid(self, set_options, caplog):
        value = object()
        config = set_options({"sort": value})
        assert config.options["sort"] == galleryviewer.main.OPTION_DEFAULTS["sort"]
        assert str(value) in caplog.text

    @pytest.mark.parametrize(
        ("value", "result_expected"),
        {"ignore": True, "consider": False, "invalid": None}.items(),
    )
    @pytest.mark.parametrize("opt_key", ["case", "Case"])
    def test_case_actions(self, set_options, caplog, opt_key, value, result_expected):
        config = set_options({opt_key: value})
        if result_expected is None:
            assert value in caplog.text
        else:
            assert config.options["ignore_case"] == result_expected

    @pytest.mark.parametrize(
        ("value", "result_expected"),
        {
            **configparser.ConfigParser.BOOLEAN_STATES,
            "True": True,
            "False": False,
            "not a Boolean": None,
        }.items(),
    )
    @pytest.mark.parametrize("opt_key", ["test", "Test"])
    def test_test_boolean(self, set_options, caplog, opt_key, value, result_expected):
        config = set_options({opt_key: value})
        if result_expected is None:
            assert value in caplog.text
        else:
            assert config.options["test"] == result_expected

    @pytest.mark.parametrize(
        ("opt_key", "dest", "value"),
        [
            ("data_file", "data_file", str(object())),
            ("DataFile", "data_file", str(object())),
            ("Profile", "profile", str(object())),
        ],
    )
    def test_string_options(self, set_options, opt_key, dest, value):
        config = set_options({opt_key: value})
        assert config.options[dest] == value
