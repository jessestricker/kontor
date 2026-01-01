import errno
import logging
import re
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING

import click
import dacite

if TYPE_CHECKING:
    from collections.abc import Iterator
    from typing import Literal, Self

_CONFIG_FILE_NAME = ".kontor.toml"
_KONTOR_DIR_NAME = ".kontor"

_logger = logging.getLogger(__name__)

type _SyncState = Literal["synced", "missing", "conflict"]


class Kontor:
    def __init__(self) -> None:
        self._home_dir = Path.home()
        self._config = _Config.from_file(self._home_dir / _CONFIG_FILE_NAME)

    @property
    def _kontor_dir(self) -> Path:
        return self._home_dir / _KONTOR_DIR_NAME

    @property
    def _profile_dir(self) -> Path:
        return self._kontor_dir / self._config.profile

    def _files(self) -> Iterator[Path]:
        for dir_path, _, file_names in self._profile_dir.walk():
            for file_name in file_names:
                yield dir_path / file_name

    def __repr__(self) -> str:
        attrs = (f"{name}={value!r}" for name, value in self.__dict__.items())
        return f"{self.__class__.__qualname__}({', '.join(attrs)})"

    def link(self, home_file: Path) -> None:
        # resolve home file's parent dir, removing '..' segments
        home_file = _resolve_parent(home_file)
        _logger.debug("home_file=%r", home_file)

        # fail if home file path is in kontor dir
        if home_file.is_relative_to(self._kontor_dir):
            msg = "file must not be from kontor directory"
            raise ValueError(msg)

        # get relative path to home dir
        # also fail if home file path is not in home dir
        try:
            relative_path = home_file.relative_to(self._home_dir)
        except ValueError:
            msg = "file must be from home directory"
            raise ValueError(msg) from None

        # build kontor file path
        kontor_file = self._profile_dir / relative_path
        _logger.debug("kontor_file=%r", kontor_file)

        # fail if home file is already linked into kontor dir
        if kontor_file.exists():
            msg = "file already exists in kontor"
            raise ValueError(msg)

        # link home file into kontor
        _logger.info("linking %r into kontor", str(home_file))
        kontor_file.parent.mkdir(parents=True, exist_ok=True)
        home_file.move(kontor_file)
        home_file.symlink_to(kontor_file)

    def list(self) -> None:
        _logger.info("listing files in the kontor...")
        for file_path in self._files():
            relative_path = file_path.relative_to(self._profile_dir)
            click.echo(relative_path)

    def sync(self) -> bool:
        all_ok = True
        for kontor_file in self._files():
            if not self._sync_file(kontor_file):
                all_ok = False
                # but do continue with syncing files

        return all_ok

    def _sync_file(self, kontor_file: Path) -> bool:
        relative_path = kontor_file.relative_to(self._profile_dir)
        home_file = self._home_dir / relative_path
        state = self._get_sync_state(kontor_file, home_file)

        match state:
            case "synced":
                click.echo(f"{home_file} - {click.style('OK', fg='green')}")
                return True

            case "missing":
                home_file.parent.mkdir(parents=True, exist_ok=True)
                home_file.symlink_to(kontor_file)
                click.echo(f"{home_file} - {click.style('SYNCED', fg='blue')}")
                return True

            case "conflict":
                click.echo(f"{home_file} - {click.style('CONFLICT', fg='red')}")
                return False

    def _get_sync_state(self, kontor_file: Path, home_file: Path) -> _SyncState:
        try:
            home_file_target = home_file.readlink()
        except FileNotFoundError:
            # home file does not exist
            return "missing"
        except OSError as exc:
            if exc.errno == errno.EINVAL:
                # home file is not a symbolic link
                return "conflict"

            raise

        if home_file_target != kontor_file:
            # home file is a link but does not point to kontor file
            return "conflict"

        return "synced"


def _resolve_parent(path: Path) -> Path:
    parent = path.parent.resolve(strict=True)
    return parent / path.name


_PROFILE_PATTERN = re.compile(r"[a-zA-Z0-9_-]+")


@dataclass
class _Config:
    profile: str

    def __post_init__(self) -> None:
        if not _PROFILE_PATTERN.fullmatch(self.profile):
            msg = f"profile does not match {_PROFILE_PATTERN.pattern}"
            raise ValueError(msg)

    @classmethod
    def from_file(cls, path: Path) -> Self:
        with path.open(mode="rb") as file:
            data = tomllib.load(file)

        return dacite.from_dict(cls, data)
