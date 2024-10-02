import argparse
import logging
import os
import shutil
from pathlib import Path

from resilio_companion.api import ResilioAPI
from resilio_companion.utils.ignore import compile_ruleset, rules_to_set

logger = logging.Logger(__name__)


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
    client = ResilioAPI.from_ini(args.config)
    folders = client.get_sync_folders()

    print(folders[0])
    print([f["path"] for f in folders])

    for f in folders:
        update_ignore(Path(f["path"]), delete=args.delete, dry_run=args.dry_run)


def update_ignore(p: Path, delete: bool = True, dry_run: bool = False) -> None:
    local_ignore_path = p / ".sync/IgnoreList"
    global_ignore_path = p / "resilio-ignore.txt"

    if not global_ignore_path.exists():
        logger.info(f"Folder {p} does not have a resilio-ignore.txt file.")
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
    logger.info(f"Ignore list changed at {p}, replacing in .sync folder.")
    with open(global_ignore_path) as f:
        with open(local_ignore_path, "w") as g:
            g.write(f.read())

    if delete:
        pattern = compile_ruleset(global_rules)
        for path in p.glob("**"):
            path_str = "/" + str(path.as_posix())
            if pattern.findall(path_str):
                logger.info(f"Deleting {path}")
                if dry_run:
                    continue
                if path.is_file():
                    os.remove(path)
                elif path.is_dir():
                    shutil.rmtree(path)
