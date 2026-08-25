import json

from persistence.safe_storage import SafeStorage


def test_save_and_load_json(tmp_path):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={},
    )

    data = {
        "battery": 72,
        "charging": False,
        "context": {
            "active": True,
        },
    }

    storage.save(data)

    assert path.exists()

    loaded = storage.load()

    assert loaded == data


def test_nested_data_is_preserved(tmp_path):
    path = tmp_path / "nested" / "state.json"

    storage = SafeStorage(
        path,
        default={},
    )

    data = {
        "context": {
            "screen": {
                "active": True,
            },
            "network": {
                "connected": True,
            },
        },
        "history": [
            {
                "battery": 90,
            },
            {
                "battery": 80,
            },
        ],
    }

    storage.save(data)

    assert storage.load() == data


def test_json_is_valid_after_save(tmp_path):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={},
    )

    storage.save(
        {
            "value": 123,
        }
    )

    with path.open(
        "r",
        encoding="utf-8",
    ) as file:
        parsed = json.load(file)

    assert parsed == {
        "value": 123,
    }


def test_custom_validator_accepts_valid_data(tmp_path):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={},
        validator=lambda data: (
            isinstance(data, dict)
            and "battery" in data
        ),
    )

    storage.save(
        {
            "battery": 50,
        }
    )

    assert storage.load() == {
        "battery": 50,
    }


def test_invalid_data_is_not_persisted(tmp_path):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={},
        validator=lambda data: (
            isinstance(data, dict)
            and "battery" in data
        ),
    )

    assert storage.save_if_valid(
        {
            "invalid": True,
        }
    ) is False

    assert not path.exists()


def test_existing_valid_data_is_replaced_atomically(
    tmp_path,
):
    path = tmp_path / "state.json"

    storage = SafeStorage(
        path,
        default={},
    )

    storage.save(
        {
            "version": 1,
        }
    )

    storage.save(
        {
            "version": 2,
        }
    )

    assert storage.load() == {
        "version": 2,
    }


def test_mutable_default_is_not_shared(tmp_path):
    path = tmp_path / "missing.json"

    default = {
        "items": [],
    }

    storage = SafeStorage(
        path,
        default=default,
    )

    first = storage.load()
    first["items"].append("changed")

    second = storage.load()

    assert second == {
        "items": [],
    }