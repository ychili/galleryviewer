#!/bin/sh

_EXE="galleryviewer"
_TEST_PATHS='1.jpg 10.jpg 2.jpg'

_test_version() { $_EXE --version; }

_test_help() { $_EXE --help; }

_test_check_sort() {
  $_EXE --check-sort $_TEST_PATHS
}

_test_check_sort_output() {
  CMD="$_EXE --check-sort $_TEST_PATHS"

  if test "$($CMD --sort=none)" != "$(printf %s\\n $_TEST_PATHS)"
  then return 1; fi
  if test "$($CMD --sort=ascii)" != "$(printf %s\\n $_TEST_PATHS)"
  then return 1; fi
  if test "$($CMD --sort=human)" != "$(printf %s\\n 1.jpg 2.jpg 10.jpg)"
  then return 1; fi
  return 0
}

_test_builtin_profiles() {
  profiles="builtin builtin/default.html builtin/dark.html"

  for arg in $profiles; do
    cmdline="$_EXE --no-test --profile $arg $_TEST_PATHS"
    if ! $cmdline >/dev/null
    then
      echo "Command exited with non-zero status: $cmdline"
      return 1
    fi
  done
  return 0
}

_test_output() {
  outfile="$(mktemp)"
  title='My-Awesome-Gallery'
  cmdline="$_EXE --no-test --profile builtin --title $title $_TEST_PATHS"

  if ! $cmdline > "$outfile"
  then
    echo "Command exited with non-zero status: $cmdline"
    echo "Output is in $outfile"
    return 1
  fi
  for word in '</html>' "$title" 'pageIndex' '#content'; do
    if ! grep -q "$word" "$outfile"; then
      echo "Expected string $word not found in output."
      echo "Output is in $outfile"
      return 1
    fi
  done
  rm "$outfile"
  return 0
}

_TESTS="_test_version _test_help _test_check_sort _test_check_sort_output
        _test_builtin_profiles _test_output"

_main() {
  output="$(mktemp)"

  for func in $_TESTS; do
    if "$func" > "$output"
    then
      echo "  [32mPASS[0m: $func returned $?"
    else
      echo "  [31mFAIL[0m: $func returned $?"
      echo "    stdout ($output):"
      cat "$output"
      return 1
    fi
  done

  # Remove on success
  rm "$output"
}

_main
