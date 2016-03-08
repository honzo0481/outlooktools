''' tests for findunscheduledappts.py'''

import os
import tempfile
import unittest

from findunscheduledappts import (loadcsv, StringProcessor, f_chainer,
    get_most_similar)

class LoadcsvTest(unittest.TestCase):

    def setUp(self):
        self.temp = tempfile.NamedTemporaryFile(delete=False)
        self.temp.write('00,01,02,03\r\n'
                        '10,11,12,13\r\n'
                        '20,21,22,23')
        self.temp.seek(0)

    def tearDown(self):
        self.temp.close()
        os.remove(self.temp.name)

    def test_load_adjacent_fields(self):
        self.assertEqual([['01','02'],
                          ['11','12'],
                          ['21','22']],
                          loadcsv(self.temp.name, usecols=[1,2]))

    def test_load_all_fields(self):
        self.assertEqual([['00','01','02','03'],
                          ['10','11','12','13'],
                          ['20','21','22','23']],
                          loadcsv(self.temp.name))

    def test_load_nonadjacent_fields(self):
        self.assertEqual([['00','02'],
                          ['10','12'],
                          ['20','22']],
                          loadcsv(self.temp.name, usecols=[0,2]))

    def test_load_one_field(self):
        self.assertEqual([['00'],
                          ['10'],
                          ['20']],
                          loadcsv(self.temp.name, usecols=[0]))


class StringProcessorTest(unittest.TestCase):

    def setUp(self):
        self.sp = StringProcessor()

    def test_default_blacklist_characters(self):
        self.assertEqual('1 2',
            self.sp.normalize('1!@#$%^&*()_+-=\\|;:\'",<.>/?2'))

    def test_delete_single_characters(self):
        self.assertEqual(' bb  ', self.sp.delete_single_characters('a bb c d'))

    def test_nondefault_blacklist_characters(self):
        self.assertEqual('!@# $%',
            self.sp.normalize('!@#aabbc$%', blacklist='abc'))

    def test_tokenize_empty_string(self):
        self.assertEqual([], self.sp.tokenize(''))

    def test_tokenize_single_word(self):
        self.assertEqual(['word'], self.sp.tokenize('word'))

    def test_tokenize_multiple_words(self):
        self.assertEqual(['two', 'words'], self.sp.tokenize('words two'))


class FChainerTest(unittest.TestCase):

    def setUp(self):
        self.sp = StringProcessor()
        self.string = ['aut perferendis doloribus asperiores repellat']
        self.string_tokens = [['asperiores', 'aut', 'doloribus', 'perferendis',
                              'repellat']]
        self.strings = ['lorem ipsum dolor sit amet', 'consectetur adipiscing elit',
                        'sed do tempor incididunt']
        self.strings_tokens = [['amet', 'dolor', 'ipsum', 'lorem', 'sit'],
                               ['adipiscing', 'consectetur', 'elit'],
                               ['do', 'incididunt', 'sed', 'tempor']]
        self.functions1 = [self.sp.delete_single_characters, self.sp.normalize]
        self.functions2 = [self.sp.tokenize]

    # as in `a = a`, mathematically reflexive
    def test_f_chainer_single_string_reflexive(self):
        self.assertEqual(self.string,
            f_chainer(self.string, self.functions1))

    def test_f_chainer_multi_string_reflexive(self):
        self.assertEqual(self.strings,
            f_chainer(self.strings, self.functions1))

    def test_f_chainer_single_string(self):
        self.assertEqual(self.string_tokens,
            f_chainer(self.string, self.functions1 + self.functions2))

    def test_f_chainer_multi_string(self):
        self.assertEqual(self.strings_tokens,
            f_chainer(self.strings, self.functions1 + self.functions2))

class GetMostSimilarTest(unittest.TestCase):

    def test_get_most_similar_default_metric_reflexive(self):
        self.assertEqual((1.0, 'aaa'), get_most_similar('aaa', ['aaa', 'bbb']))

if __name__ == '__main__':
    unittest.main()
