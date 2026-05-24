"""Midas — a minimal, opinionated static site generator."""

from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("midas-ssg")
except PackageNotFoundError:
    __version__ = "0.0.0"
