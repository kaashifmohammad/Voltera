import json

from persistence.safe_storage import (
    PersistenceValidationError,
    PersistenceWriteError,
    SafeStorage,
)


def test_malformed_json_is_contained(tmp_path):
    path = tmp_path / "corrupt.json"

    path.write_text(
        '{"battery": 50,',
        encoding="utf-8",
    )

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


def test_corrupt_json_does_not_escape_as_json_error(
    tmp_path,
):
    path = tmp_path / "corrupt.json"

    path.write_text(
        "not-json-at-all",
        encoding="utf-8",
    )

    storage = SafeStorage(
        path,
        default={},
    )

    result = storage.load()

    assert result == {}


def test_strict_mode_rejects_corrupt_json(
    tmp_path,
):
    path = tmp_path / "corrupt.json"

    path.write_text(
        "{broken",
        encoding="utf-8",
    )

    storage = SafeStorage(
        path,
        default={},
    )

    try:
        storage.load_strict()
    except Exception as exc:
        assert type(exc).__name__ == (
            "PersistenceReadError"
        )
    else:
        raise AssertionError(
            "Expected strict loading to fail"
        )


def test_invalid_structure_returns_fallback(
    tmp_path,
):
    path = tmp_path / "state.json"

    path.write_text(
        json.dumps(
            {
                "wrong": "structure",
            }
        ),
        encoding="utf-8",
    )

    storage = SafeStorage(
        path,
        default={
            "battery": None,
        },
        validator=lambda data: (
            isinstance(data, dict)
            and isinstance(
                data.get("battery"),
                (int, float),
            )
        ),
    )

    assert storage.load() == {
        "battery": None,
    }


def test_strict_mode_rejects_invalid_structure(
    tmp_path,
):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={},
        validator=lambda data: (
            isinstance(data, dict)
            and "required" in data
        ),
    )

    storage.save(
        {
            "required": True,
        }
    )

    path.write_text(
        json.dumps(
            {
                "invalid": True,
            }
        ),
        encoding="utf-8",
    )

    try:
        storage.load_strict()
    except PersistenceValidationError:
        pass
    else:
        raise AssertionError(
            "Expected PersistenceValidationError"
        )


def test_non_serializable_data_is_rejected(
    tmp_path,
):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={},
    )

    try:
        storage.save(
            {
                "invalid": object(),
            }
        )
    except PersistenceWriteError:
        pass
    else:
        raise AssertionError(
            "Expected PersistenceWriteError"
        )


def test_previous_valid_file_survives_failed_serialization(
    tmp_path,
):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={},
    )

    original = {
        "battery": 80,
    }

    storage.save(original)

    try:
        storage.save(
            {
                "battery": object(),
            }
        )
    except PersistenceWriteError:
        pass

    assert storage.load() == original


def test_validator_exception_is_contained(
    tmp_path,
):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={
            "fallback": True,
        },
        validator=lambda data: (
            1 / 0
        ),
    )

    assert storage.load() == {
        "fallback": True,
    }


def test_valid_data_remains_available_after_corruption_repair(
    tmp_path,
):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={
            "battery": None,
        },
    )

    storage.save(
        {
            "battery": 75,
        }
    )

    path.write_text(
        "CORRUPTED",
        encoding="utf-8",
    )

    recovered = storage.recover(
        repair=True,
    )

    assert recovered == {
        "battery": None,
    }

    assert storage.load() == {
        "battery": None,
    }