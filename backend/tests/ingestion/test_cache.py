from app.ingestion.cache import FileCache


def test_miss_then_hit(tmp_path):
    cache = FileCache(directory=tmp_path, ttl_seconds=3600)
    assert cache.get("fuelhh_2026-01-01") is None

    cache.set("fuelhh_2026-01-01", [{"a": 1}])
    assert cache.get("fuelhh_2026-01-01") == [{"a": 1}]


def test_expired_entry_is_a_miss(tmp_path):
    cache = FileCache(directory=tmp_path, ttl_seconds=0)
    cache.set("key", [{"a": 1}])
    assert cache.get("key") is None


def test_corrupt_entry_is_a_miss_not_a_crash(tmp_path):
    cache = FileCache(directory=tmp_path, ttl_seconds=3600)
    path = cache._path_for("key")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("{not valid json", encoding="utf-8")

    assert cache.get("key") is None


def test_colon_in_key_is_sanitized_for_windows_filenames(tmp_path):
    cache = FileCache(directory=tmp_path, ttl_seconds=3600)
    cache.set("fuelhh_2026-01-01T00:00:00+00:00", [{"a": 1}])
    assert cache.get("fuelhh_2026-01-01T00:00:00+00:00") == [{"a": 1}]
