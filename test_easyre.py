from re import error
from unittest import TestCase as _TestCase

from lib.easyre import (
    Text,
    Or,
    Group,
    Many,
    CharacterSet,
    CharacterRange,
    NegativeCharacterSet,
    NegativeCharacterRange,
    NumericRange,
)


class TestCase(_TestCase):

    def set(self, re):
        self.re = re

    def yes(self, *args):
        if len(args) == 1:
            re = self.re
            s = args[0]
        else:
            re, s = args
        try:
            self.assertTrue(
                re.match_exact(s),
                msg='%s does not match %r' % (
                    re, s))

            re = re.optimize()
            self.assertTrue(
                re.match_exact(s),
                msg='%s does not match %r' % (
                    re, s))
        except error as e:
            self.fail('could not compile %s: %r' % (re, e))

    def no(self, *args):
        if len(args) == 1:
            re = self.re
            s = args[0]
        else:
            re, s = args
        try:
            self.assertFalse(
                re.match_exact(s),
                msg='%s should not match %r' % (
                    re, s))

            re = re.optimize()

            self.assertFalse(
                re.match_exact(s),
                msg='%s does not match %r' % (
                    re, s))
        except error as e:
            self.fail('count not compile %s: %r' % (re, e))


class TestBasics(TestCase):

    def test_character_range(self):
        self.yes(CharacterRange('af'), 'e')
        self.no(CharacterRange('af'), 'z')

    def test_escape(self):
        self.set(Text('\\"'))
        self.assertEqual(len('\\"'), 2)
        self.yes('\\"')

    def test_complicated(self):
        self.set((Text('\\"') | NegativeCharacterSet('"')).many())
        self.yes('\\"abc\\"foo')
        self.no('"')

    def test_negative_character_range(self):
        self.yes(NegativeCharacterRange('af'), 'z')
        self.no(NegativeCharacterRange('af'), 'e')

    def test_character_set(self):
        self.yes(CharacterSet('abcdef'), 'e')
        self.yes(CharacterSet('^abcdef'), 'e')
        self.yes(CharacterSet('^abcdef'), '^')
        self.no(CharacterSet('abcdef'), 'g')
        self.no(CharacterSet('abcdef'), '^')

    def test_negative_character_set(self):
        self.yes(NegativeCharacterSet('abcdef'), 'z')
        self.yes(NegativeCharacterSet('abcdef'), '^')
        self.no(NegativeCharacterSet('^abcdef'), '^')
        self.no(NegativeCharacterSet('a^bcdef'), '^')
        self.no(NegativeCharacterSet('abcdef'), 'b')

    def test_match_text(self):
        self.yes(Text('foobar'), 'foobar')
        self.no(Text('foobar'), 'foo')
        self.no(Text('foobar'), '')

    def test_maybe(self):
        self.set(Text('foobar').maybe())
        self.yes('foobar')
        self.yes('')
        self.no('foobarfoobar')

    def test_multiplication(self):
        self.set(Text('foobar') * 2)
        self.no('foobar')
        self.yes('foobar' * 2)
        self.no('foobar' * 3)

    def test_range_multiplication(self):
        self.set(Text('foobar').mult(1,2)*3)
        self.no('foobar' * 1)
        self.no('foobar' * 2)
        self.yes('foobar' * 3)
        self.yes('foobar' * 4)
        self.yes('foobar' * 5)
        self.yes('foobar' * 6)
        self.no('foobar' * 7)

    def test_range(self):
        self.set(Text('foobar').mult(2, 3))
        self.no('foobar')
        self.yes('foobar' * 2)
        self.yes('foobar' * 3)
        self.no('foobar' * 4)

    def test_star(self):
        self.set(Text('foobar').star())
        self.yes('')
        self.no('foo')
        self.yes('foobar')
        self.yes('foobar' * 10)

    def test_append(self):
        self.set(Text('foo') + Text('bar'))
        self.yes('foobar')
        self.no('foo')
        self.no('bar')

    def test_or(self):
        self.set(Text('foo') | Text('bar'))
        self.no('foobar')
        self.yes('foo')
        self.yes('bar')

    def test_many_0_inf(self):
        self.set(Text('foo').mult())
        self.no('fo')
        self.no('foofo')
        self.yes('foo')
        self.yes('foofoo')
        self.yes('')
        self.yes('foofoofoo')
        self.yes('foo' * 1000)
        self.no('oo' + 'foo' * 1000)

    def test_many_0_1(self):
        self.set(Text('foo').mult(0, 1))
        self.yes('')
        self.yes('foo' * 1)
        self.no('foo' * 2)

    def test_many_0_2(self):
        self.set(Text('foo').mult(0, 2))
        self.yes('')
        self.yes('foo')
        self.yes('foo' * 2)
        self.no('foo' * 3)

    def test_many_1_inf(self):
        self.set(Text('foo').mult(1))
        self.no('')
        self.yes('foo' * 1)
        self.yes('foo' * 10)
        self.no('oo' + 'foo' * 10)

    def test_many_3_4(self):
        self.set(Text('foo').mult(3, 4))
        self.no('foo' * 2)
        self.yes('foo' * 3)
        self.yes('foo' * 4)
        self.no('foo' * 5)

    def test_or(self):
        self.set(Text('foo') + (Text('bar') | Text('boo')))
        self.no('foo')
        self.no('foobarboo')
        self.yes('foobar')
        self.yes('fooboo')

    def test_numeric_range_zeropad(self):
        self.set(NumericRange(9, 11, zeropad=True))
        self.no('8')
        self.no('08')
        self.yes('9')
        self.yes('09')
        self.yes('10')
        self.no('11')

    def test_numeric_range_no_zeropad(self):
        self.set(NumericRange(9, 11, zeropad=False))
        self.no('8')
        self.no('08')
        self.yes('9')
        self.no('09')
        self.yes('10')
        self.no('11')

