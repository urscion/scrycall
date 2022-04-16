from argparse import Namespace
import unittest

from scrycall.cli import _parser, query, ArgumentError
import scrycall


class TestQueryParsing(unittest.TestCase):
    p = _parser()
    command = "query"

    def test_name_only(self):
        args = self.__class__.p.parse_args(
            [self.__class__.command, "venser", "t:creature"]
        )
        self.assertEqual(args.query, ["venser", "t:creature"])

    def test_attribute_name(self):
        args = self.__class__.p.parse_args(
            [self.__class__.command, "shock", "--format", "%n %r"]
        )
        self.assertEqual(args.formatting, "%n %r")

    def test_default_null(self):
        args = self.__class__.p.parse_args([self.__class__.command, "shock"])
        self.assertEqual(args.null, "")

    def test_custom_null(self):
        args = self.__class__.p.parse_args(
            [self.__class__.command, "shock", "--null", "na"]
        )
        self.assertEqual(args.null, "na")


class TestQueries(unittest.TestCase):
    def test_noquery(self):
        with self.assertRaises(ArgumentError):
            query(Namespace(query=[], func=query))
