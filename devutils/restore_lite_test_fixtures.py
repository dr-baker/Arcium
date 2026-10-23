#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""Restore known patch inputs omitted from Chromium's lite source archive."""

import argparse
import os
import re
import tempfile
from pathlib import Path

import validate_patches

CHROMIUM_REPOSITORY = 'https://chromium.googlesource.com/chromium/src'
FIXTURES = (
    Path('chrome/test/data/webui/cr_elements/cr_profile_avatar_selector_test.ts'),
    Path('chrome/test/data/webui/signin/test_manage_profiles_browser_proxy.ts'),
    Path('chrome/test/data/webui/signin/test_profile_customization_browser_proxy.ts'),
)


def restore_missing_fixtures(tree, version):
    """Fetch absent inputs from the selected release tag without replacing files."""
    if not re.fullmatch(r'\d+\.\d+\.\d+\.\d+', version):
        raise ValueError('Expected an exact Chromium release version')
    tree = tree.resolve(strict=True)
    missing = []
    for relative in FIXTURES:
        target = tree / relative
        if target.is_symlink() or not target.resolve().is_relative_to(tree):
            raise ValueError(f'Fixture path must stay inside the source tree: {relative}')
        if target.exists():
            if not target.is_file():
                raise ValueError(f'Fixture path is not a file: {relative}')
        else:
            missing.append(relative)
    if not missing:
        return []

    # Reuse the validator's pinned Gitiles transport and retry policy.
    # pylint: disable=protected-access
    with validate_patches._get_requests_session() as session:
        contents = {
            relative: validate_patches._download_googlesource_file(session, CHROMIUM_REPOSITORY,
                                                                   f'refs/tags/{version}', relative)
            for relative in missing
        }
    if any(not content for content in contents.values()):
        raise ValueError('Chromium returned an empty test fixture')

    # Finish downloads before publishing any file. Exclusive links prevent a
    # concurrent creator from being overwritten and never expose partial bytes.
    with tempfile.TemporaryDirectory(prefix='.arcium-fixtures-', dir=tree) as staging:
        for index, (relative, content) in enumerate(contents.items()):
            target = tree / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            if not target.resolve().is_relative_to(tree):
                raise ValueError(f'Fixture path left the source tree: {relative}')
            staged = Path(staging) / str(index)
            staged.write_bytes(content.encode('UTF-8'))
            os.link(staged, target)
    return missing


def main():
    """Restore missing fixtures in an unpacked, unpatched source tree."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree', type=Path, required=True)
    args = parser.parse_args()
    version = (Path(__file__).resolve().parent.parent / 'chromium_version.txt').read_text().strip()
    for relative in restore_missing_fixtures(args.tree, version):
        print(f'Restored Chromium {version} test fixture: {relative}')


if __name__ == '__main__':
    main()
