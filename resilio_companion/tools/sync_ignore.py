import argparse
import logging
import os
import re
import shutil
from pathlib import Path

from resilio_companion.api import ResilioAPI
from resilio_companion.utils.ignore import compile_ruleset, rules_to_set


def get_subparser(subparser: argparse.ArgumentParser):
    subparser.description = "Sync a share's ignore file into the local folder and remove any newly ignored files/folders."
    subparser.add_argument("--config", "-c", default="config.ini")
    subparser.add_argument(
        "--delete",
        "-d",
        action="store_true",
        help="Delete matched files if ignore list changed.",
    )
    subparser.add_argument(
        "--dry-run",
        "-r",
        action="store_true",
        help="Do not delete any files, only log.",
    )
    subparser.set_defaults(func=main)


def main(args):
    if args.config:
        client = ResilioAPI.from_ini(args.config)
    else:
        client = ResilioAPI.from_env()
    folders = client.get_sync_folders()

    for f in folders:
        update_ignore(Path(f["path"]), delete=args.delete, dry_run=args.dry_run)


def update_ignore(p: Path, delete: bool = True, dry_run: bool = False) -> None:
    local_ignore_path = p / ".sync/IgnoreList"
    global_ignore_path = p / "resilio-ignore.txt"

    if not global_ignore_path.exists():
        logging.info(f"Folder {p} does not have a resilio-ignore.txt file.")
        return

    with open(local_ignore_path) as f:
        text = f.read()
        local_rules = text.split("\n")

    with open(global_ignore_path) as f:
        text = f.read()
        global_rules = text.split("\n")

    # Double check if anything has changed
    local_set = rules_to_set(local_rules)
    global_set = rules_to_set(global_rules)

    if local_set == global_set:
        return

    # Things have changed, override the local with the global set
    logging.info(f"Ignore list changed at {p}, replacing in .sync folder.")
    if not dry_run:
        with open(global_ignore_path) as f:
            with open(local_ignore_path, "w") as g:
                g.write(f.read())

    if delete:
        pattern = compile_ruleset(global_rules)
        logging.debug(pattern.pattern)
        for path in p.glob("**/*"):
            delete_path(p, path, pattern, dry_run)
        for path in p.glob("**"):
            delete_path(p, path, pattern, dry_run)


def delete_path(parent: Path, path: Path, pattern: re.Pattern, dry_run: bool = False):
    relative_path = path.relative_to(parent)
    path_str = "/" + str(relative_path.as_posix())
    if path_str.startswith("/.sync"):
        return
    if pattern.findall(path_str):
        logging.info(f"Deleting {relative_path}")
        if dry_run:
            return
        if path.is_file():
            os.remove(path)
        elif path.is_dir():
            shutil.rmtree(path)
