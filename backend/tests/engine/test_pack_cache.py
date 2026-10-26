"""
The packs' JSON copies (catalogue.CACHE_DIR), written when the image is built: every pack reads back from its copy
exactly as from its YAML, a changed pack never meets an old copy, and a broken copy falls back to the YAML.
"""
from __future__ import annotations

import pytest

from campus_engine import catalogue


@pytest.fixture
def cache(tmp_path, monkeypatch):
    monkeypatch.setattr(catalogue, "CACHE_DIR", tmp_path / "cache")
    return tmp_path / "cache"


def test_every_pack_reads_back_from_its_copy_exactly_as_from_its_yaml(cache):
    assert catalogue.build_cache() == len(catalogue._packs()) > 30
    for path, model in catalogue._packs():
        copy = catalogue._cached(path.read_bytes(), model)
        assert copy.is_file(), path.name
        assert catalogue._load(path, model) == catalogue._load(path, model, use_cache=False), path.name


def test_the_loaders_use_the_copy(cache, monkeypatch):
    catalogue.build_cache()
    monkeypatch.setattr(catalogue, "_parse", lambda _text: pytest.fail("parsed YAML although a copy exists"))
    assert catalogue.load_catalogue() and catalogue.load_maps() and catalogue.load_funding() and catalogue.load_colleges()


def test_a_changed_pack_never_meets_an_old_copy(cache, tmp_path):
    path, model = next((p, m) for p, m in catalogue._packs() if m is catalogue.University)
    catalogue.build_cache()
    changed = tmp_path / path.name
    changed.write_text(path.read_text(encoding="utf-8") + "\n# edited\n", encoding="utf-8")
    assert not catalogue._cached(changed.read_bytes(), model).exists()
    assert catalogue._load(changed, model) == catalogue._load(path, model, use_cache=False)


def test_a_broken_copy_falls_back_to_the_yaml(cache):
    path, model = catalogue._packs()[0]
    catalogue.build_cache()
    catalogue._cached(path.read_bytes(), model).write_text('{"not": "a pack"}', encoding="utf-8")
    assert catalogue._load(path, model) == catalogue._load(path, model, use_cache=False)


def test_a_broken_pack_still_fails_with_its_name(cache, tmp_path):
    bad = tmp_path / "zz-broken.yaml"
    bad.write_text("university: x\n", encoding="utf-8")
    with pytest.raises(catalogue.DataPackError, match="zz-broken.yaml"):
        catalogue.load_university(bad)
