from __future__ import annotations
import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable


class PersistenceError(Exception):
    """Base exception for persistence failures."""


class PersistenceReadError(PersistenceError):
    """Raised when persisted data cannot be read safely."""


class PersistenceWriteError(PersistenceError):
    """Raised when persisted data cannot be written safely."""


class PersistenceValidationError(PersistenceError):
    """Raised when persisted data has an invalid structure."""


Validator = Callable[[Any], bool]


class SafeStorage:
    """
    Reliable JSON persistence layer for VOLTERA.

    Responsibilities:
    - Safely load JSON data.
    - Handle missing files.
    - Handle empty files.
    - Detect malformed JSON.
    - Validate loaded structures.
    - Provide safe fallback values.
    - Write atomically to avoid partially written files.
    - Preserve a previous valid file when a write fails.
    """

    def __init__(
        self,
        path: str | Path,
        *,
        default: Any = None,
        validator: Validator | None = None,
        create_parent: bool = True,
    ) -> None:
        self.path = Path(path)
        self.default = default
        self.validator = validator
        self.create_parent = create_parent

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def exists(self) -> bool:
        """Return whether the persistence file exists."""
        return self.path.exists()

    def load(
        self,
        *,
        fallback: Any = None,
        validate: bool = True,
    ) -> Any:
        """
        Safely load persisted JSON data.

        Missing, empty, malformed, or invalid data returns the
        configured fallback instead of crashing the caller.
        """

        effective_fallback = (
            self.default
            if fallback is None
            else fallback
        )

        if not self.path.exists():
            return self._copy_default(
                effective_fallback
            )

        try:
            raw = self.path.read_text(
                encoding="utf-8"
            )

            if not raw.strip():
                return self._copy_default(
                    effective_fallback
                )

            data = json.loads(raw)

        except (OSError, UnicodeError, json.JSONDecodeError):
            return self._copy_default(
                effective_fallback
            )

        if validate and self.validator is not None:
            try:
                valid = bool(
                    self.validator(data)
                )
            except Exception:
                valid = False

            if not valid:
                return self._copy_default(
                    effective_fallback
                )

        return data

    def load_strict(
        self,
        *,
        validate: bool = True,
    ) -> Any:
        """
        Strict load operation.

        Unlike load(), this method raises a typed persistence
        exception when stored data cannot be safely loaded.
        """

        if not self.path.exists():
            raise PersistenceReadError(
                f"Persistence file does not exist: "
                f"{self.path}"
            )

        try:
            raw = self.path.read_text(
                encoding="utf-8"
            )

            if not raw.strip():
                raise PersistenceReadError(
                    f"Persistence file is empty: "
                    f"{self.path}"
                )

            data = json.loads(raw)

        except json.JSONDecodeError as exc:
            raise PersistenceReadError(
                f"Invalid JSON in persistence file: "
                f"{self.path}"
            ) from exc

        except (OSError, UnicodeError) as exc:
            raise PersistenceReadError(
                f"Unable to read persistence file: "
                f"{self.path}"
            ) from exc

        if validate and self.validator is not None:
            try:
                valid = bool(
                    self.validator(data)
                )
            except Exception as exc:
                raise PersistenceValidationError(
                    f"Persistence validation failed: "
                    f"{self.path}"
                ) from exc

            if not valid:
                raise PersistenceValidationError(
                    f"Persisted data has an invalid "
                    f"structure: {self.path}"
                )

        return data

    def save(
        self,
        data: Any,
        *,
        validate: bool = True,
        indent: int = 2,
    ) -> None:
        """
        Atomically persist JSON data.

        The data is first written to a temporary file in the
        destination directory and then atomically replaced into
        place.
        """

        if validate and self.validator is not None:
            try:
                valid = bool(
                    self.validator(data)
                )
            except Exception as exc:
                raise PersistenceValidationError(
                    "Persistence validation failed "
                    "before write."
                ) from exc

            if not valid:
                raise PersistenceValidationError(
                    "Refusing to persist invalid data."
                )

        self._ensure_parent()

        try:
            serialized = json.dumps(
                data,
                indent=indent,
                ensure_ascii=False,
                sort_keys=True,
            )
        except (TypeError, ValueError) as exc:
            raise PersistenceWriteError(
                "Data is not JSON serializable."
            ) from exc

        temporary_path: Path | None = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=self.path.parent,
                prefix=f".{self.path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temporary:
                temporary.write(serialized)
                temporary.flush()
                os.fsync(
                    temporary.fileno()
                )
                temporary_path = Path(
                    temporary.name
                )

            os.replace(
                temporary_path,
                self.path,
            )

            temporary_path = None

        except (OSError, UnicodeError) as exc:
            raise PersistenceWriteError(
                f"Unable to write persistence file: "
                f"{self.path}"
            ) from exc

        finally:
            if (
                temporary_path is not None
                and temporary_path.exists()
            ):
                try:
                    temporary_path.unlink()
                except OSError:
                    pass

    def save_if_valid(
        self,
        data: Any,
        *,
        indent: int = 2,
    ) -> bool:
        """
        Validate and persist data.

        Returns True on success and False when persistence
        validation fails.
        """

        try:
            self.save(
                data,
                validate=True,
                indent=indent,
            )
        except PersistenceError:
            return False

        return True

    def recover(
        self,
        *,
        fallback: Any = None,
        repair: bool = False,
    ) -> Any:
        """
        Load data with recovery semantics.

        If the stored file is missing, empty, malformed, or
        invalid, the fallback is returned.

        When repair=True, the fallback is also persisted as a
        fresh valid JSON document.
        """

        effective_fallback = (
            self.default
            if fallback is None
            else fallback
        )

        data = self.load(
            fallback=effective_fallback,
            validate=True,
        )

        if repair and not self._is_valid(data):
            self.save(
                effective_fallback,
                validate=False,
            )
            return self._copy_default(
                effective_fallback
            )

        return data

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def validate(self, data: Any) -> bool:
        """
        Return whether data satisfies the configured validator.
        """

        if self.validator is None:
            return True

        try:
            return bool(
                self.validator(data)
            )
        except Exception:
            return False

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _ensure_parent(self) -> None:
        if not self.create_parent:
            return

        try:
            self.path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )
        except OSError as exc:
            raise PersistenceWriteError(
                f"Unable to create persistence "
                f"directory: {self.path.parent}"
            ) from exc

    def _is_valid(self, data: Any) -> bool:
        if self.validator is None:
            return True

        try:
            return bool(
                self.validator(data)
            )
        except Exception:
            return False

    @staticmethod
    def _copy_default(value: Any) -> Any:
        """
        Return a completely independent fallback object.

        A deep copy is required because VOLTERA persistence data
        can contain nested dictionaries, lists, and other mutable
        structures.
        """

        return copy.deepcopy(value)