import argparse
import sys

from . import data
from . import output


class ArgumentError(Exception):
    """Error with input arguments"""


def main() -> int:
    parser = _parser()
    parsed_args = parser.parse_args()
    return parsed_args.func(parsed_args)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Scryfall CLI",
        epilog=(
            "%n    name"
            "\n%m    mana_cost"
            "\n%c    cmc  (converted mana cost)"
            "\n%y    type_line"
            "\n%p    power"
            "\n%t    toughness"
            "\n%l    loyalty"
            "\n%o    oracle_text"
            "\n%f    flavor_text"
            "\n%%    this will print a literal % instead of interpreting a special character"
            "\n%|    this will separate output into nicely spaced columns"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    subparsers = parser.add_subparsers(dest="command")

    query_parser = subparsers.add_parser("query")
    query_parser.set_defaults(func=query)
    query_parser.add_argument(
        "query",
        nargs="*",
        metavar="query",
        default=[],
        help="Scryfall query",
    )
    query_parser.add_argument(
        "--format",
        dest="formatting",
        type=str,
        default=(
            f"{output.Attributes.NAME.value}"
            f" %| {output.Attributes.TYPE_LINE.value}"
            f" %| {output.Attributes.CMC.value}"
        ),
    )
    query_parser.add_argument(
        "--null",
        dest="null",
        default="",
        help="Print this value when NULL is the property value",
    )
    query_parser.add_argument(
        "--cache-only",
        action="store_true",
        help="Query the local cache only (No API)",
    )
    query_parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Query the API only (No cache)",
    )
    query_parser.add_argument(
        "--skip-caching",
        action="store_true",
        help="Skip writing to the cache (Not recommended)",
    )

    cache_parser = subparsers.add_parser("cache")
    cache_parser.set_defaults(func=cache)
    cache_parser.add_argument(
        "--prune",
        action="store_true",
        help="Search the local cache and delete any stale data.",
    )
    cache_parser.add_argument(
        "--purge",
        action="store_true",
        help="Delete everything from the local cache.",
    )

    return parser


def query(args: argparse.Namespace) -> int:
    args.query = " ".join(args.query)
    args.query.replace("`", "'")

    if not args.query:
        _parser().print_help()
        raise ArgumentError("No query provided!")
    if args.cache_only and args.no_cache:
        raise ArgumentError("Cannot specify to only use both cache and API.")

    # TODO: Pass these as a group of arguments for better testability?
    if args.skip_caching:
        data.CAN_WRITE_CACHE = False
    if args.no_cache:
        data.CAN_READ_CACHE = False
    if args.cache_only:
        data.USE_API = False

    output.CUSTOM_NULL = args.null

    cards = data.get_cards_from_query(args.query)
    if not cards:
        print("No cards found!", file=sys.stderr)
        return 1
    output.print_cards(cards, args.formatting)
    return 0


def cache(args: argparse.Namespace) -> int:
    if args.prune:
        data.URL_CACHE.prune()
        data.CARD_CACHE.prune()
    if args.purge:
        data.URL_CACHE.purge()
        data.CARD_CACHE.purge()
    return 0
