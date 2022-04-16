#!/usr/bin/env python3
import sys

from scrycall.cli import main as cli_main


def main() -> int:
    return cli_main(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
