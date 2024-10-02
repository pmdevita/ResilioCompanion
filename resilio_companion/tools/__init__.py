import argparse

from .sync_ignore import get_subparser as sync_ignore_subparser

parser = argparse.ArgumentParser(
    description="Various tools to help run a Resilio Sync server"
)
subparsers = parser.add_subparsers()
sync_ignore_subparser(subparsers.add_parser("ignore"))


def main():
    args = parser.parse_args()

    if not args:
        parser.print_help()
        return

    if not hasattr(args, "func"):
        parser.print_help()
        return

    args.func(args)


if __name__ == "__main__":
    main()
