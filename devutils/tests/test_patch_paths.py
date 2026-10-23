# Copyright 2026 The Arcium Authors
# You can use, redistribute, and/or modify this source code under
# the terms of the GPL-3.0 license that can be found in the LICENSE file.
"""Logical paths for Git and Quilt patch headers."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'third_party'))
import unidiff # pylint: disable=wrong-import-position

sys.path.pop(0)


@pytest.mark.parametrize('source_prefix,target_prefix', [('a/', 'b/'), ('src.orig/', 'src/')])
@pytest.mark.parametrize('change', ['modify', 'add', 'delete'])
def test_patch_path(source_prefix, target_prefix, change):
    """Both header formats identify the same file, including /dev/null cases."""
    logical_path = 'components/example.txt'
    source = '/dev/null' if change == 'add' else source_prefix + logical_path
    target = '/dev/null' if change == 'delete' else target_prefix + logical_path
    hunks = {
        'modify': '@@ -1 +1 @@\n-old\n+new\n',
        'add': '@@ -0,0 +1 @@\n+new\n',
        'delete': '@@ -1 +0,0 @@\n-old\n',
    }
    patched_file = unidiff.PatchSet(f'--- {source}\n+++ {target}\n{hunks[change]}')[0]

    assert patched_file.path == logical_path
    assert patched_file.source_file == source
    assert patched_file.target_file == target
    assert patched_file.is_added_file == (change == 'add')
    assert patched_file.is_removed_file == (change == 'delete')


@pytest.mark.parametrize('source,target',
                         [('components/example.txt', 'components/example.txt'),
                          ('src.orig/components/example.txt', 'b/components/example.txt')])
def test_unrecognized_header_pair_preserves_source_path(source, target):
    """Only the recognized paired prefixes are stripped from modifications."""
    patched_file = unidiff.PatchSet(f'--- {source}\n+++ {target}\n@@ -1 +1 @@\n-old\n+new\n')[0]

    assert patched_file.path == source
