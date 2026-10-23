# -*- coding: UTF-8 -*-
"""Known lite omissions are restored from the exact release without data loss."""

import sys
from pathlib import Path
from unittest import mock

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import restore_lite_test_fixtures as fixtures

sys.path.pop(0)

VERSION = '151.0.7922.71'


def test_restore_pins_tag_and_preserves_existing_file(tmp_path):
    """Only missing files are fetched and their exact bytes are retained."""
    existing = tmp_path / fixtures.FIXTURES[0]
    existing.parent.mkdir(parents=True)
    existing.write_bytes(b'local fixture\n')
    with mock.patch.object(fixtures.validate_patches, '_get_requests_session') as session, \
         mock.patch.object(fixtures.validate_patches, '_download_googlesource_file',
                           return_value='upstream fixture\n') as download:
        restored = fixtures.restore_missing_fixtures(tmp_path, VERSION)
        assert restored == list(fixtures.FIXTURES[1:])
        assert existing.read_bytes() == b'local fixture\n'
        for relative in restored:
            assert (tmp_path / relative).read_bytes() == b'upstream fixture\n'
            download.assert_any_call(session.return_value.__enter__.return_value,
                                     fixtures.CHROMIUM_REPOSITORY, f'refs/tags/{VERSION}', relative)
        download.reset_mock()
        session.reset_mock()
        assert not fixtures.restore_missing_fixtures(tmp_path, VERSION)
        download.assert_not_called()
        session.assert_not_called()


def test_download_failure_publishes_no_files(tmp_path):
    """A later unavailable input leaves all missing inputs absent."""
    with mock.patch.object(fixtures.validate_patches, '_get_requests_session'), \
         mock.patch.object(fixtures.validate_patches, '_download_googlesource_file',
                           side_effect=['first\n', RuntimeError('unavailable')]):
        with pytest.raises(RuntimeError, match='unavailable'):
            fixtures.restore_missing_fixtures(tmp_path, VERSION)
    assert not any((tmp_path / relative).exists() for relative in fixtures.FIXTURES)


def test_invalid_version_does_not_download(tmp_path):
    """Never fall back to HEAD or a different release."""
    with mock.patch.object(fixtures.validate_patches, '_get_requests_session') as session:
        with pytest.raises(ValueError, match='exact Chromium'):
            fixtures.restore_missing_fixtures(tmp_path, 'HEAD')
        session.assert_not_called()


def test_symlink_cannot_escape_tree(tmp_path):
    """An input symlink cannot redirect writes into another tree."""
    tree = tmp_path / 'source'
    outside = tmp_path / 'outside'
    tree.mkdir()
    outside.mkdir()
    (tree / 'chrome').symlink_to(outside, target_is_directory=True)
    with pytest.raises(ValueError, match='inside the source tree'):
        fixtures.restore_missing_fixtures(tree, VERSION)
    assert not list(outside.iterdir())


def test_concurrent_file_is_not_overwritten(tmp_path):
    """An input created during download wins over our stale missing-file check."""
    target = tmp_path / fixtures.FIXTURES[0]

    def download(*_args):
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b'concurrent fixture\n')
        return 'downloaded\n'

    with mock.patch.object(fixtures.validate_patches, '_get_requests_session'), \
         mock.patch.object(fixtures.validate_patches, '_download_googlesource_file',
                           side_effect=download):
        with pytest.raises(FileExistsError):
            fixtures.restore_missing_fixtures(tmp_path, VERSION)
    assert target.read_bytes() == b'concurrent fixture\n'


def test_empty_response_is_rejected(tmp_path):
    """An empty success response must not become a bogus patch input."""
    with mock.patch.object(fixtures.validate_patches, '_get_requests_session'), \
         mock.patch.object(fixtures.validate_patches, '_download_googlesource_file',
                           return_value=''):
        with pytest.raises(ValueError, match='empty test fixture'):
            fixtures.restore_missing_fixtures(tmp_path, VERSION)
    assert not any((tmp_path / relative).exists() for relative in fixtures.FIXTURES)


def test_gateway_retries_are_bounded_and_missing_files_are_not_retried(tmp_path):
    """Retry transient upstream failures without hiding an invalid release path."""
    # pylint: disable=protected-access
    session = fixtures.validate_patches._get_requests_session()
    with mock.patch.object(fixtures.validate_patches, '_get_requests_session',
                           return_value=session), \
         mock.patch.object(fixtures.validate_patches, '_download_googlesource_file',
                           return_value='fixture\n'):
        fixtures.restore_missing_fixtures(tmp_path, VERSION)
    retries = session.get_adapter(fixtures.CHROMIUM_REPOSITORY).max_retries
    assert retries.total == 3
    assert retries.is_retry('GET', 502)
    assert retries.is_retry('GET', 504)
    assert not retries.is_retry('GET', 404)
