# -*- coding: UTF-8 -*-

# Copyright (c) 2020 The ungoogled-chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE.ungoogled_chromium file.
"""Test validate_patches.py"""

import logging
import tempfile
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / 'utils'))
from _common import ENCODING, get_logger, set_logging_level

sys.path.pop(0)

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import validate_patches

sys.path.pop(0)


def test_test_patches():
    """Test _dry_check_patched_file"""

    #pylint: disable=protected-access
    set_logging_level(logging.DEBUG)

    orig_file_content = """bye world"""
    series_iter = ['test.patch']

    def _run_test_patches(patch_content):
        with tempfile.TemporaryDirectory() as tmpdirname:
            Path(tmpdirname, 'foobar.txt').write_text(orig_file_content, encoding=ENCODING)
            Path(tmpdirname, 'test.patch').write_text(patch_content, encoding=ENCODING)
            _, patch_cache = validate_patches._load_all_patches(series_iter, Path(tmpdirname))
            required_files = validate_patches._get_required_files(patch_cache)
            files_under_test = validate_patches._retrieve_local_files(required_files,
                                                                      Path(tmpdirname))
            return validate_patches._test_patches(series_iter, patch_cache, files_under_test)

    get_logger().info('Check valid modification')
    patch_content = """--- a/foobar.txt
+++ b/foobar.txt
@@ -1 +1 @@
-bye world
+hello world
"""
    assert not _run_test_patches(patch_content)

    get_logger().info('Check invalid modification')
    patch_content = """--- a/foobar.txt
+++ b/foobar.txt
@@ -1 +1 @@
-hello world
+olleh world
"""
    assert _run_test_patches(patch_content)

    get_logger().info('Check correct removal')
    patch_content = """--- a/foobar.txt
+++ /dev/null
@@ -1 +0,0 @@
-bye world
"""
    assert not _run_test_patches(patch_content)

    get_logger().info('Check incorrect removal')
    patch_content = """--- a/foobar.txt
+++ /dev/null
@@ -1 +0,0 @@
-this line does not exist in foobar
"""
    assert _run_test_patches(patch_content)


def _apply_fixture(patch, content):
    """Apply a synthetic file patch through the production validator."""
    # pylint: disable=protected-access
    parsed = validate_patches.unidiff.PatchSet(patch.splitlines(keepends=True))[0]
    lines = content.split('\n')
    validate_patches._modify_file_lines(parsed, lines)
    return '\n'.join(lines)


def test_exact_offset_is_carried_to_later_hunks():
    """Accept moved context without changing which source lines are removed."""
    patch = """--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,4 @@
 anchor
-old
+new
+extra
 end
@@ -6,3 +7,3 @@
 later
-remove
+replacement
 tail
"""
    source = 'prefix\nanchor\nold\nend\ngap1\ngap2\nlater\nremove\ntail\n'
    assert _apply_fixture(
        patch,
        source) == ('prefix\nanchor\nnew\nextra\nend\ngap1\ngap2\nlater\nreplacement\ntail\n')


def test_exact_recorded_position_wins_over_other_matches():
    """An unchanged recorded position identifies its occurrence unambiguously."""
    patch = """--- a/file.txt
+++ b/file.txt
@@ -1 +1 @@
-old
+new
"""
    assert _apply_fixture(patch, 'old\nold\n') == 'new\nold\n'


def test_offset_rejects_ambiguous_or_changed_context():
    """Never guess between two moved matches or drop mismatched context."""
    # pylint: disable=protected-access
    patch = """--- a/file.txt
+++ b/file.txt
@@ -1,3 +1,3 @@
 anchor
-old
+new
 end
"""
    for source in ('prefix\nanchor\nold\nend\nanchor\nold\nend\n', 'changed-anchor\nold\nend\n'):
        with pytest.raises(validate_patches._PatchValidationError):
            _apply_fixture(patch, source)


def test_unanchored_insertion_cannot_escape_source_bounds():
    """Reject a source-free insertion whose declared position does not exist."""
    # pylint: disable=protected-access
    patch = """--- a/file.txt
+++ b/file.txt
@@ -99,0 +100 @@
+new
"""
    with pytest.raises(validate_patches._PatchValidationError):
        _apply_fixture(patch, 'old\n')


def test_verbose_diagnostic_preserves_source_newlines(monkeypatch):
    """Diagnostic patch receives the same multiline source that failed validation."""
    # pylint: disable=protected-access
    set_logging_level(logging.DEBUG)
    patch = """--- a/file.txt
+++ b/file.txt
@@ -1,2 +1,2 @@
 first
-wrong
+new
"""
    seen = []
    monkeypatch.setattr(validate_patches, '_dry_check_patched_file',
                        lambda _patch, content: seen.append(content) or 'diagnostic')
    parsed = validate_patches.unidiff.PatchSet(patch.splitlines(keepends=True))
    assert validate_patches._test_patches(['test.patch'], {'test.patch': parsed},
                                          {Path('file.txt'): ['first', 'second', '']})
    assert seen == ['first\nsecond\n']


def test_zero_length_targets_use_deletion_coordinates():
    """A +N,0 deletion starts after line N, including the beginning of a file."""
    patch = """--- a/file.txt
+++ b/file.txt
@@ -1 +0,0 @@
-remove
@@ -3 +1,0 @@
-remove
"""
    assert _apply_fixture(patch, 'remove\nkeep\nremove\ntail\n') == 'keep\ntail\n'


def test_adjacent_hunks_can_change_size_without_double_counting_offsets():
    """An exact relocation carries through adjacent growing and shrinking hunks."""
    patch = """--- a/file.txt
+++ b/file.txt
@@ -1 +1,2 @@
-first
+one
+two
@@ -2 +2,0 @@
-second
"""
    assert _apply_fixture(patch, 'prefix\nfirst\nsecond\ntail\n') == ('prefix\none\ntwo\ntail\n')


def test_unanchored_insertions_respect_empty_and_eof_boundaries():
    """An EOF sentinel is not an extra source line available for insertion."""
    # pylint: disable=protected-access
    empty = """--- a/file.txt
+++ b/file.txt
@@ -0,0 +1 @@
+new
"""
    eof = """--- a/file.txt
+++ b/file.txt
@@ -1,0 +2 @@
+new
"""
    assert _apply_fixture(empty, '') == 'new\n'
    assert _apply_fixture(eof, 'old\n') == 'old\nnew\n'
    assert _apply_fixture(eof, 'old') == 'old\nnew'
    outside = eof.replace('-1,0 +2', '-2,0 +3')
    with pytest.raises(validate_patches._PatchValidationError):
        _apply_fixture(outside, 'old\n')


def test_anchored_hunk_cannot_consume_eof_sentinel():
    """A final newline does not supply a blank line for removal or context."""
    # pylint: disable=protected-access
    removal = """--- a/file.txt
+++ b/file.txt
@@ -2 +2 @@
-
+new
"""
    context = """--- a/file.txt
+++ b/file.txt
@@ -1,2 +1,2 @@
-old
+new
""" + " \n"
    for patch in (removal, context):
        with pytest.raises(validate_patches._PatchValidationError):
            _apply_fixture(patch, 'old\n')
    assert _apply_fixture(removal, 'old\n\n') == 'old\nnew\n'


if __name__ == '__main__':
    test_test_patches()


def test_added_file_preserves_final_blank_and_newline_metadata():
    """New files use the same line representation as source files read from disk."""
    # pylint: disable=protected-access
    fixtures = [
        ("+a\n+\n", 2, ['a', '', '']),
        ("+a\n", 1, ['a', '']),
        ("+a\n\\ No newline at end of file\n", 1, ['a']),
    ]
    for body, count, expected in fixtures:
        patch = f"--- /dev/null\n+++ b/file.txt\n@@ -0,0 +1,{count} @@\n{body}"
        parsed = validate_patches.unidiff.PatchSet(patch.splitlines(keepends=True))[0]
        files = {}
        validate_patches._apply_file_unidiff(parsed, files)
        assert files[Path('file.txt')] == expected
        replacement = "--- a/file.txt\n+++ b/file.txt\n@@ -2 +2 @@\n-\n+last\n"
        change = validate_patches.unidiff.PatchSet(replacement.splitlines(keepends=True))[0]
        if count == 2:
            validate_patches._apply_file_unidiff(change, files)
            assert files[Path('file.txt')] == ['a', 'last', '']
        else:
            with pytest.raises(validate_patches._PatchValidationError):
                validate_patches._apply_file_unidiff(change, files)
