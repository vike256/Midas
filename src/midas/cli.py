"""
Midas — CLI entry point.
"""

import argparse
import shutil
import sys
from pathlib import Path

from importlib.resources import files

from .core import build, serve, DIST_DIR
from .defaults import load_config


def _copy_tree(src, dst: Path) -> None:
    """Recursively copy from importlib.resources Traversable to Path."""
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            target.mkdir(exist_ok=True)
            _copy_tree(item, target)
        else:
            target.write_bytes(item.read_bytes())


STYLE_CSS_HEADER = """/* Override Midas base styles here.
   This file is loaded after midas.css, so any rule here wins.
   Delete this file if you don't need custom styles.
*/
"""


def init_project(target: Path) -> None:
    if target.exists() and any(target.iterdir()):
        print(f"Error: {target} is not empty. Midas init requires an empty directory.")
        print("Existing files in directory:")
        for item in target.iterdir():
            marker = " (dir)" if item.is_dir() else ""
            print(f"  {item.name}{marker}")
        sys.exit(1)

    target.mkdir(parents=True, exist_ok=True)
    starter = files("midas") / "starter"
    _copy_tree(starter, target)

    # Scaffold empty override files
    (target / "static").mkdir(exist_ok=True)
    (target / "static" / "style.css").write_text(STYLE_CSS_HEADER, encoding="utf-8")

    print(f"Initialized Midas project in {target}")


from . import __version__


def main() -> None:
    parser = argparse.ArgumentParser(description="Midas — static site generator")
    parser.add_argument("-v", "--version", action="version", version=f"Midas {__version__}")
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Initialize a new Midas project")
    init_parser.add_argument("folder", nargs="?", default=".", help="Target directory")

    subparsers.add_parser("build", help="Build the site to dist/")
    subparsers.add_parser("serve", help="Build and serve on localhost:8000")
    subparsers.add_parser("clean", help="Wipe dist/")

    args = parser.parse_args()

    if args.command == "init":
        init_project(Path(args.folder))
        return

    if args.command == "clean":
        if DIST_DIR.exists():
            shutil.rmtree(DIST_DIR)
        print("Cleaned dist/")
        return

    config = load_config()
    build(config)

    if args.command == "serve":
        serve()
