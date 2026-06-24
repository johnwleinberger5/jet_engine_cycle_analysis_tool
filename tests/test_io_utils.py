"""Tests for pipeline.io_utils — pickle read/write utilities."""

import pytest
from pathlib import Path
from pipeline.io_utils import read_pkl, write_pkl


def test_write_and_read_roundtrip(tmp_path):
    obj = {"key": [1, 2, 3], "nested": {"a": 1.0}}
    pkl_path = tmp_path / "test.pkl"
    write_pkl(pkl_path, obj)
    result = read_pkl(pkl_path)
    assert result == obj


def test_write_creates_parent_dirs(tmp_path):
    pkl_path = tmp_path / "subdir" / "nested" / "test.pkl"
    write_pkl(pkl_path, 42)
    assert pkl_path.exists()


def test_read_missing_file_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_pkl(tmp_path / "nonexistent.pkl")


def test_roundtrip_various_types(tmp_path):
    for obj in [None, 3.14, [1, 2], (3, 4), {5, 6}]:
        pkl_path = tmp_path / "obj.pkl"
        write_pkl(pkl_path, obj)
        assert read_pkl(pkl_path) == obj
