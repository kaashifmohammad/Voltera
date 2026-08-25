from persistence.safe_storage import (
    PersistenceReadError,
    SafeStorage,
)


def test_missing_file_returns_default(tmp_path):
    path = tmp_path / "missing.json"

    storage = SafeStorage(
        path,
        default={
            "battery": None,
        },
    )

    result = storage.load()

    assert result == {
        "battery": None,
    }


def test_missing_file_does_not_raise(tmp_path):
    path = tmp_path / "missing.json"

    storage = SafeStorage(
        path,
        default={},
    )

    result = storage.load()

    assert result == {}


def test_empty_file_returns_default(tmp_path):
    path = tmp_path / "empty.json"

    path.write_text(
        "",
        encoding="utf-8",
    )

    storage = SafeStorage(
        path,
        default={
            "recovered": True,
        },
    )

    assert storage.load() == {
        "recovered": True,
    }


def test_whitespace_only_file_returns_default(
    tmp_path,
):
    path = tmp_path / "empty.json"

    path.write_text(
        "   \n\t  ",
        encoding="utf-8",
    )

    storage = SafeStorage(
        path,
        default={
            "recovered": True,
        },
    )

    assert storage.load() == {
        "recovered": True,
    }


def test_recover_can_repair_invalid_storage(
    tmp_path,
):
    path = tmp_path / "state.json"

    path.write_text(
        "{ invalid json",
        encoding="utf-8",
    )

    storage = SafeStorage(
        path,
        default={
            "version": 1,
            "state": "reset",
        },
    )

    result = storage.recover(
        repair=True,
    )

    assert result == {
        "version": 1,
        "state": "reset",
    }

    assert storage.load() == {
        "version": 1,
        "state": "reset",
    }


def test_custom_fallback_overrides_default(tmp_path):
    path = tmp_path / "missing.json"

    storage = SafeStorage(
        path,
        default={
            "default": True,
        },
    )

    result = storage.load(
        fallback={
            "custom": True,
        }
    )

    assert result == {
        "custom": True,
    }


def test_strict_load_reports_missing_file(tmp_path):
    path = tmp_path / "missing.json"

    storage = SafeStorage(
        path,
        default={},
    )

    try:
        storage.load_strict()
    except PersistenceReadError as exc:
        assert "does not exist" in str(exc)
    else:
        raise AssertionError(
            "Expected PersistenceReadError"
        )


def test_recovery_does_not_change_valid_data(
    tmp_path,
):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={
            "fallback": True,
        },
    )

    original = {
        "battery": 64,
        "charging": False,
    }

    storage.save(original)

    recovered = storage.recover(
        repair=True,
    )

    assert recovered == original
    assert storage.load() == original