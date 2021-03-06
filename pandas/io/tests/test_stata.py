# pylint: disable=E1101

from datetime import datetime
import datetime as dt
import os
import warnings
import nose
import struct
import sys
from distutils.version import LooseVersion

import numpy as np

import pandas as pd
from pandas.compat import iterkeys
from pandas.core.frame import DataFrame, Series
from pandas.io.parsers import read_csv
from pandas.io.stata import (read_stata, StataReader, InvalidColumnName,
    PossiblePrecisionLoss, StataMissingValue)
import pandas.util.testing as tm
from pandas.tslib import NaT
from pandas.util.misc import is_little_endian
from pandas import compat

class TestStata(tm.TestCase):

    def setUp(self):
        # Unit test datasets for dta7 - dta9 (old stata formats 104, 105 and 107) can be downloaded from:
        # http://stata-press.com/data/glmext.html
        self.dirpath = tm.get_data_path()
        self.dta1_114 = os.path.join(self.dirpath, 'stata1_114.dta')
        self.dta1_117 = os.path.join(self.dirpath, 'stata1_117.dta')

        self.dta2_113 = os.path.join(self.dirpath, 'stata2_113.dta')
        self.dta2_114 = os.path.join(self.dirpath, 'stata2_114.dta')
        self.dta2_115 = os.path.join(self.dirpath, 'stata2_115.dta')
        self.dta2_117 = os.path.join(self.dirpath, 'stata2_117.dta')

        self.dta3_113 = os.path.join(self.dirpath, 'stata3_113.dta')
        self.dta3_114 = os.path.join(self.dirpath, 'stata3_114.dta')
        self.dta3_115 = os.path.join(self.dirpath, 'stata3_115.dta')
        self.dta3_117 = os.path.join(self.dirpath, 'stata3_117.dta')
        self.csv3 = os.path.join(self.dirpath, 'stata3.csv')

        self.dta4_113 = os.path.join(self.dirpath, 'stata4_113.dta')
        self.dta4_114 = os.path.join(self.dirpath, 'stata4_114.dta')
        self.dta4_115 = os.path.join(self.dirpath, 'stata4_115.dta')
        self.dta4_117 = os.path.join(self.dirpath, 'stata4_117.dta')

        self.dta7 = os.path.join(self.dirpath, 'cancer.dta')
        self.csv7 = os.path.join(self.dirpath, 'cancer.csv')

        self.dta8 = os.path.join(self.dirpath, 'tbl19-3.dta')

        self.csv8 = os.path.join(self.dirpath, 'tbl19-3.csv')

        self.dta9 = os.path.join(self.dirpath, 'lbw.dta')
        self.csv9 = os.path.join(self.dirpath, 'lbw.csv')

        self.dta_encoding = os.path.join(self.dirpath, 'stata1_encoding.dta')

        self.csv14 = os.path.join(self.dirpath, 'stata5.csv')
        self.dta14_113 = os.path.join(self.dirpath, 'stata5_113.dta')
        self.dta14_114 = os.path.join(self.dirpath, 'stata5_114.dta')
        self.dta14_115 = os.path.join(self.dirpath, 'stata5_115.dta')
        self.dta14_117 = os.path.join(self.dirpath, 'stata5_117.dta')

        self.csv15 = os.path.join(self.dirpath, 'stata6.csv')
        self.dta15_113 = os.path.join(self.dirpath, 'stata6_113.dta')
        self.dta15_114 = os.path.join(self.dirpath, 'stata6_114.dta')
        self.dta15_115 = os.path.join(self.dirpath, 'stata6_115.dta')
        self.dta15_117 = os.path.join(self.dirpath, 'stata6_117.dta')

        self.dta16_115 = os.path.join(self.dirpath, 'stata7_115.dta')
        self.dta16_117 = os.path.join(self.dirpath, 'stata7_117.dta')

        self.dta17_113 = os.path.join(self.dirpath, 'stata8_113.dta')
        self.dta17_115 = os.path.join(self.dirpath, 'stata8_115.dta')
        self.dta17_117 = os.path.join(self.dirpath, 'stata8_117.dta')

        self.dta18_115 = os.path.join(self.dirpath, 'stata9_115.dta')
        self.dta18_117 = os.path.join(self.dirpath, 'stata9_117.dta')


    def read_dta(self, file):
        # Legacy default reader configuration
        return read_stata(file, convert_dates=True)

    def read_csv(self, file):
        return read_csv(file, parse_dates=True)

    def test_read_empty_dta(self):
        empty_ds = DataFrame(columns=['unit'])
        # GH 7369, make sure can read a 0-obs dta file
        with tm.ensure_clean() as path:
            empty_ds.to_stata(path,write_index=False)
            empty_ds2 = read_stata(path)
            tm.assert_frame_equal(empty_ds, empty_ds2)

    def test_read_dta1(self):
        reader_114 = StataReader(self.dta1_114)
        parsed_114 = reader_114.data()
        reader_117 = StataReader(self.dta1_117)
        parsed_117 = reader_117.data()
        # Pandas uses np.nan as missing value.
        # Thus, all columns will be of type float, regardless of their name.
        expected = DataFrame([(np.nan, np.nan, np.nan, np.nan, np.nan)],
                             columns=['float_miss', 'double_miss', 'byte_miss',
                                      'int_miss', 'long_miss'])

        # this is an oddity as really the nan should be float64, but
        # the casting doesn't fail so need to match stata here
        expected['float_miss'] = expected['float_miss'].astype(np.float32)

        tm.assert_frame_equal(parsed_114, expected)
        tm.assert_frame_equal(parsed_117, expected)

    def test_read_dta2(self):
        if LooseVersion(sys.version) < '2.7':
            raise nose.SkipTest('datetime interp under 2.6 is faulty')

        expected = DataFrame.from_records(
            [
                (
                    datetime(2006, 11, 19, 23, 13, 20),
                    1479596223000,
                    datetime(2010, 1, 20),
                    datetime(2010, 1, 8),
                    datetime(2010, 1, 1),
                    datetime(1974, 7, 1),
                    datetime(2010, 1, 1),
                    datetime(2010, 1, 1)
                ),
                (
                    datetime(1959, 12, 31, 20, 3, 20),
                    -1479590,
                    datetime(1953, 10, 2),
                    datetime(1948, 6, 10),
                    datetime(1955, 1, 1),
                    datetime(1955, 7, 1),
                    datetime(1955, 1, 1),
                    datetime(2, 1, 1)
                ),
                (
                    pd.NaT,
                    pd.NaT,
                    pd.NaT,
                    pd.NaT,
                    pd.NaT,
                    pd.NaT,
                    pd.NaT,
                    pd.NaT,
                )
            ],
            columns=['datetime_c', 'datetime_big_c', 'date', 'weekly_date',
                     'monthly_date', 'quarterly_date', 'half_yearly_date',
                     'yearly_date']
        )
        expected['yearly_date'] = expected['yearly_date'].astype('O')

        with warnings.catch_warnings(record=True) as w:
            parsed_114 = self.read_dta(self.dta2_114)
            parsed_115 = self.read_dta(self.dta2_115)
            parsed_117 = self.read_dta(self.dta2_117)
            # 113 is buggy due ot limits date format support in Stata
            # parsed_113 = self.read_dta(self.dta2_113)

            # should get a warning for that format.
            tm.assert_equal(len(w), 1)

        # buggy test because of the NaT comparison on certain platforms
        # Format 113 test fails since it does not support tc and tC formats
        # tm.assert_frame_equal(parsed_113, expected)
        tm.assert_frame_equal(parsed_114, expected)
        tm.assert_frame_equal(parsed_115, expected)
        tm.assert_frame_equal(parsed_117, expected)

    def test_read_dta3(self):
        parsed_113 = self.read_dta(self.dta3_113)
        parsed_114 = self.read_dta(self.dta3_114)
        parsed_115 = self.read_dta(self.dta3_115)
        parsed_117 = self.read_dta(self.dta3_117)

        # match stata here
        expected = self.read_csv(self.csv3)
        expected = expected.astype(np.float32)
        expected['year'] = expected['year'].astype(np.int16)
        expected['quarter'] = expected['quarter'].astype(np.int8)

        tm.assert_frame_equal(parsed_113, expected)
        tm.assert_frame_equal(parsed_114, expected)
        tm.assert_frame_equal(parsed_115, expected)
        tm.assert_frame_equal(parsed_117, expected)

    def test_read_dta4(self):
        parsed_113 = self.read_dta(self.dta4_113)
        parsed_114 = self.read_dta(self.dta4_114)
        parsed_115 = self.read_dta(self.dta4_115)
        parsed_117 = self.read_dta(self.dta4_117)

        expected = DataFrame.from_records(
            [
                ["one", "ten", "one", "one", "one"],
                ["two", "nine", "two", "two", "two"],
                ["three", "eight", "three", "three", "three"],
                ["four", "seven", 4, "four", "four"],
                ["five", "six", 5, np.nan, "five"],
                ["six", "five", 6, np.nan, "six"],
                ["seven", "four", 7, np.nan, "seven"],
                ["eight", "three", 8, np.nan, "eight"],
                ["nine", "two", 9, np.nan, "nine"],
                ["ten", "one", "ten", np.nan, "ten"]
            ],
            columns=['fully_labeled', 'fully_labeled2', 'incompletely_labeled',
                     'labeled_with_missings', 'float_labelled'])

        # these are all categoricals
        expected = pd.concat([expected[col].astype('category') for col in expected], axis=1)

        tm.assert_frame_equal(parsed_113, expected)
        tm.assert_frame_equal(parsed_114, expected)
        tm.assert_frame_equal(parsed_115, expected)
        tm.assert_frame_equal(parsed_117, expected)

    def test_read_write_dta5(self):
        original = DataFrame([(np.nan, np.nan, np.nan, np.nan, np.nan)],
                             columns=['float_miss', 'double_miss', 'byte_miss',
                                      'int_miss', 'long_miss'])
        original.index.name = 'index'

        with tm.ensure_clean() as path:
            original.to_stata(path, None)
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  original)

    def test_write_dta6(self):
        original = self.read_csv(self.csv3)
        original.index.name = 'index'
        original.index = original.index.astype(np.int32)
        original['year'] = original['year'].astype(np.int32)
        original['quarter'] = original['quarter'].astype(np.int32)

        with tm.ensure_clean() as path:
            original.to_stata(path, None)
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  original)

    @nose.tools.nottest
    def test_read_dta7(self):
        expected = read_csv(self.csv7, parse_dates=True, sep='\t')
        parsed = self.read_dta(self.dta7)
        tm.assert_frame_equal(parsed, expected)

    @nose.tools.nottest
    def test_read_dta8(self):
        expected = read_csv(self.csv8, parse_dates=True, sep='\t')
        parsed = self.read_dta(self.dta8)
        tm.assert_frame_equal(parsed, expected)

    @nose.tools.nottest
    def test_read_dta9(self):
        expected = read_csv(self.csv9, parse_dates=True, sep='\t')
        parsed = self.read_dta(self.dta9)
        tm.assert_frame_equal(parsed, expected)

    def test_read_write_dta10(self):
        original = DataFrame(data=[["string", "object", 1, 1.1,
                                    np.datetime64('2003-12-25')]],
                             columns=['string', 'object', 'integer', 'floating',
                                      'datetime'])
        original["object"] = Series(original["object"], dtype=object)
        original.index.name = 'index'
        original.index = original.index.astype(np.int32)
        original['integer'] = original['integer'].astype(np.int32)

        with tm.ensure_clean() as path:
            original.to_stata(path, {'datetime': 'tc'})
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  original)

    def test_stata_doc_examples(self):
        with tm.ensure_clean() as path:
            df = DataFrame(np.random.randn(10, 2), columns=list('AB'))
            df.to_stata(path)

    def test_encoding(self):

        # GH 4626, proper encoding handling
        raw = read_stata(self.dta_encoding)
        encoded = read_stata(self.dta_encoding, encoding="latin-1")
        result = encoded.kreis1849[0]

        if compat.PY3:
            expected = raw.kreis1849[0]
            self.assertEqual(result, expected)
            self.assertIsInstance(result, compat.string_types)
        else:
            expected = raw.kreis1849.str.decode("latin-1")[0]
            self.assertEqual(result, expected)
            self.assertIsInstance(result, unicode)

        with tm.ensure_clean() as path:
            encoded.to_stata(path,encoding='latin-1', write_index=False)
            reread_encoded = read_stata(path, encoding='latin-1')
            tm.assert_frame_equal(encoded, reread_encoded)

    def test_read_write_dta11(self):
        original = DataFrame([(1, 2, 3, 4)],
                             columns=['good', compat.u('b\u00E4d'), '8number', 'astringwithmorethan32characters______'])
        formatted = DataFrame([(1, 2, 3, 4)],
                              columns=['good', 'b_d', '_8number', 'astringwithmorethan32characters_'])
        formatted.index.name = 'index'
        formatted = formatted.astype(np.int32)

        with tm.ensure_clean() as path:
            with warnings.catch_warnings(record=True) as w:
                original.to_stata(path, None)
                # should get a warning for that format.
            tm.assert_equal(len(w), 1)

            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'), formatted)

    def test_read_write_dta12(self):
        original = DataFrame([(1, 2, 3, 4, 5, 6)],
                             columns=['astringwithmorethan32characters_1',
                                      'astringwithmorethan32characters_2',
                                      '+',
                                      '-',
                                      'short',
                                      'delete'])
        formatted = DataFrame([(1, 2, 3, 4, 5, 6)],
                              columns=['astringwithmorethan32characters_',
                                       '_0astringwithmorethan32character',
                                       '_',
                                       '_1_',
                                       '_short',
                                       '_delete'])
        formatted.index.name = 'index'
        formatted = formatted.astype(np.int32)

        with tm.ensure_clean() as path:
            with warnings.catch_warnings(record=True) as w:
                original.to_stata(path, None)
                tm.assert_equal(len(w), 1)  # should get a warning for that format.

            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'), formatted)

    def test_read_write_dta13(self):
        s1 = Series(2**9, dtype=np.int16)
        s2 = Series(2**17, dtype=np.int32)
        s3 = Series(2**33, dtype=np.int64)
        original = DataFrame({'int16': s1, 'int32': s2, 'int64': s3})
        original.index.name = 'index'

        formatted = original
        formatted['int64'] = formatted['int64'].astype(np.float64)

        with tm.ensure_clean() as path:
            original.to_stata(path)
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  formatted)

    def test_read_write_reread_dta14(self):
        expected = self.read_csv(self.csv14)
        cols = ['byte_', 'int_', 'long_', 'float_', 'double_']
        for col in cols:
            expected[col] = expected[col].convert_objects(convert_numeric=True)
        expected['float_'] = expected['float_'].astype(np.float32)
        expected['date_td'] = pd.to_datetime(expected['date_td'], coerce=True)

        parsed_113 = self.read_dta(self.dta14_113)
        parsed_113.index.name = 'index'
        parsed_114 = self.read_dta(self.dta14_114)
        parsed_114.index.name = 'index'
        parsed_115 = self.read_dta(self.dta14_115)
        parsed_115.index.name = 'index'
        parsed_117 = self.read_dta(self.dta14_117)
        parsed_117.index.name = 'index'

        tm.assert_frame_equal(parsed_114, parsed_113)
        tm.assert_frame_equal(parsed_114, parsed_115)
        tm.assert_frame_equal(parsed_114, parsed_117)

        with tm.ensure_clean() as path:
            parsed_114.to_stata(path, {'date_td': 'td'})
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'), parsed_114)

    def test_read_write_reread_dta15(self):
        expected = self.read_csv(self.csv15)
        expected['byte_'] = expected['byte_'].astype(np.int8)
        expected['int_'] = expected['int_'].astype(np.int16)
        expected['long_'] = expected['long_'].astype(np.int32)
        expected['float_'] = expected['float_'].astype(np.float32)
        expected['double_'] = expected['double_'].astype(np.float64)
        expected['date_td'] = expected['date_td'].apply(datetime.strptime, args=('%Y-%m-%d',))

        parsed_113 = self.read_dta(self.dta15_113)
        parsed_114 = self.read_dta(self.dta15_114)
        parsed_115 = self.read_dta(self.dta15_115)
        parsed_117 = self.read_dta(self.dta15_117)

        tm.assert_frame_equal(expected, parsed_114)
        tm.assert_frame_equal(parsed_113, parsed_114)
        tm.assert_frame_equal(parsed_114, parsed_115)
        tm.assert_frame_equal(parsed_114, parsed_117)

    def test_timestamp_and_label(self):
        original = DataFrame([(1,)], columns=['var'])
        time_stamp = datetime(2000, 2, 29, 14, 21)
        data_label = 'This is a data file.'
        with tm.ensure_clean() as path:
            original.to_stata(path, time_stamp=time_stamp, data_label=data_label)
            reader = StataReader(path)
            parsed_time_stamp = dt.datetime.strptime(reader.time_stamp, ('%d %b %Y %H:%M'))
            assert parsed_time_stamp == time_stamp
            assert reader.data_label == data_label

    def test_numeric_column_names(self):
        original = DataFrame(np.reshape(np.arange(25.0), (5, 5)))
        original.index.name = 'index'
        with tm.ensure_clean() as path:
            # should get a warning for that format.
            with warnings.catch_warnings(record=True) as w:
                tm.assert_produces_warning(original.to_stata(path), InvalidColumnName)
            # should produce a single warning
            tm.assert_equal(len(w), 1)

            written_and_read_again = self.read_dta(path)
            written_and_read_again = written_and_read_again.set_index('index')
            columns = list(written_and_read_again.columns)
            convert_col_name = lambda x: int(x[1])
            written_and_read_again.columns = map(convert_col_name, columns)
            tm.assert_frame_equal(original, written_and_read_again)

    def test_nan_to_missing_value(self):
        s1 = Series(np.arange(4.0), dtype=np.float32)
        s2 = Series(np.arange(4.0), dtype=np.float64)
        s1[::2] = np.nan
        s2[1::2] = np.nan
        original = DataFrame({'s1': s1, 's2': s2})
        original.index.name = 'index'
        with tm.ensure_clean() as path:
            original.to_stata(path)
            written_and_read_again = self.read_dta(path)
            written_and_read_again = written_and_read_again.set_index('index')
            tm.assert_frame_equal(written_and_read_again, original)

    def test_no_index(self):
        columns = ['x', 'y']
        original = DataFrame(np.reshape(np.arange(10.0), (5, 2)),
                             columns=columns)
        original.index.name = 'index_not_written'
        with tm.ensure_clean() as path:
            original.to_stata(path, write_index=False)
            written_and_read_again = self.read_dta(path)
            tm.assertRaises(KeyError,
                            lambda: written_and_read_again['index_not_written'])

    def test_string_no_dates(self):
        s1 = Series(['a', 'A longer string'])
        s2 = Series([1.0, 2.0], dtype=np.float64)
        original = DataFrame({'s1': s1, 's2': s2})
        original.index.name = 'index'
        with tm.ensure_clean() as path:
            original.to_stata(path)
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  original)

    def test_large_value_conversion(self):
        s0 = Series([1, 99], dtype=np.int8)
        s1 = Series([1, 127], dtype=np.int8)
        s2 = Series([1, 2 ** 15 - 1], dtype=np.int16)
        s3 = Series([1, 2 ** 63 - 1], dtype=np.int64)
        original = DataFrame({'s0': s0, 's1': s1, 's2': s2, 's3': s3})
        original.index.name = 'index'
        with tm.ensure_clean() as path:
            with warnings.catch_warnings(record=True) as w:
                tm.assert_produces_warning(original.to_stata(path),
                                           PossiblePrecisionLoss)
            # should produce a single warning
            tm.assert_equal(len(w), 1)

            written_and_read_again = self.read_dta(path)
            modified = original.copy()
            modified['s1'] = Series(modified['s1'], dtype=np.int16)
            modified['s2'] = Series(modified['s2'], dtype=np.int32)
            modified['s3'] = Series(modified['s3'], dtype=np.float64)
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  modified)

    def test_dates_invalid_column(self):
        original = DataFrame([datetime(2006, 11, 19, 23, 13, 20)])
        original.index.name = 'index'
        with tm.ensure_clean() as path:
            with warnings.catch_warnings(record=True) as w:
                tm.assert_produces_warning(original.to_stata(path, {0: 'tc'}),
                                           InvalidColumnName)
            tm.assert_equal(len(w), 1)

            written_and_read_again = self.read_dta(path)
            modified = original.copy()
            modified.columns = ['_0']
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  modified)

    def test_date_export_formats(self):
        columns = ['tc', 'td', 'tw', 'tm', 'tq', 'th', 'ty']
        conversions = dict(((c, c) for c in columns))
        data = [datetime(2006, 11, 20, 23, 13, 20)] * len(columns)
        original = DataFrame([data], columns=columns)
        original.index.name = 'index'
        expected_values = [datetime(2006, 11, 20, 23, 13, 20),  # Time
                           datetime(2006, 11, 20),  # Day
                           datetime(2006, 11, 19),  # Week
                           datetime(2006, 11, 1),  # Month
                           datetime(2006, 10, 1),  # Quarter year
                           datetime(2006, 7, 1),  # Half year
                           datetime(2006, 1, 1)]  # Year

        expected = DataFrame([expected_values], columns=columns)
        expected.index.name = 'index'
        with tm.ensure_clean() as path:
            original.to_stata(path, conversions)
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  expected)

    def test_write_missing_strings(self):
        original = DataFrame([["1"], [None]], columns=["foo"])
        expected = DataFrame([["1"], [""]], columns=["foo"])
        expected.index.name = 'index'
        with tm.ensure_clean() as path:
            original.to_stata(path)
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  expected)

    def test_bool_uint(self):
        s0 = Series([0, 1, True], dtype=np.bool)
        s1 = Series([0, 1, 100], dtype=np.uint8)
        s2 = Series([0, 1, 255], dtype=np.uint8)
        s3 = Series([0, 1, 2 ** 15 - 100], dtype=np.uint16)
        s4 = Series([0, 1, 2 ** 16 - 1], dtype=np.uint16)
        s5 = Series([0, 1, 2 ** 31 - 100], dtype=np.uint32)
        s6 = Series([0, 1, 2 ** 32 - 1], dtype=np.uint32)

        original = DataFrame({'s0': s0, 's1': s1, 's2': s2, 's3': s3,
                              's4': s4, 's5': s5, 's6': s6})
        original.index.name = 'index'
        expected = original.copy()
        expected_types = (np.int8, np.int8, np.int16, np.int16, np.int32,
                          np.int32, np.float64)
        for c, t in zip(expected.columns, expected_types):
            expected[c] = expected[c].astype(t)

        with tm.ensure_clean() as path:
            original.to_stata(path)
            written_and_read_again = self.read_dta(path)
            written_and_read_again = written_and_read_again.set_index('index')
            tm.assert_frame_equal(written_and_read_again, expected)

    def test_variable_labels(self):
        sr_115 = StataReader(self.dta16_115).variable_labels()
        sr_117 = StataReader(self.dta16_117).variable_labels()
        keys = ('var1', 'var2', 'var3')
        labels = ('label1', 'label2', 'label3')
        for k,v in compat.iteritems(sr_115):
            self.assertTrue(k in sr_117)
            self.assertTrue(v == sr_117[k])
            self.assertTrue(k in keys)
            self.assertTrue(v in labels)

    def test_minimal_size_col(self):
        str_lens = (1, 100, 244)
        s = {}
        for str_len in str_lens:
            s['s' + str(str_len)] = Series(['a' * str_len, 'b' * str_len, 'c' * str_len])
        original = DataFrame(s)
        with tm.ensure_clean() as path:
            original.to_stata(path, write_index=False)
            sr = StataReader(path)
            variables = sr.varlist
            formats = sr.fmtlist
            for variable, fmt in zip(variables, formats):
                self.assertTrue(int(variable[1:]) == int(fmt[1:-1]))

    def test_excessively_long_string(self):
        str_lens = (1, 244, 500)
        s = {}
        for str_len in str_lens:
            s['s' + str(str_len)] = Series(['a' * str_len, 'b' * str_len, 'c' * str_len])
        original = DataFrame(s)
        with tm.assertRaises(ValueError):
            with tm.ensure_clean() as path:
                original.to_stata(path)

    def test_missing_value_generator(self):
        types = ('b','h','l')
        df = DataFrame([[0.0]],columns=['float_'])
        with tm.ensure_clean() as path:
            df.to_stata(path)
            valid_range = StataReader(path).VALID_RANGE
        expected_values = ['.' + chr(97 + i) for i in range(26)]
        expected_values.insert(0, '.')
        for t in types:
            offset = valid_range[t][1]
            for i in range(0,27):
                val = StataMissingValue(offset+1+i)
                self.assertTrue(val.string == expected_values[i])

        # Test extremes for floats
        val = StataMissingValue(struct.unpack('<f',b'\x00\x00\x00\x7f')[0])
        self.assertTrue(val.string == '.')
        val = StataMissingValue(struct.unpack('<f',b'\x00\xd0\x00\x7f')[0])
        self.assertTrue(val.string == '.z')

        # Test extremes for floats
        val = StataMissingValue(struct.unpack('<d',b'\x00\x00\x00\x00\x00\x00\xe0\x7f')[0])
        self.assertTrue(val.string == '.')
        val = StataMissingValue(struct.unpack('<d',b'\x00\x00\x00\x00\x00\x1a\xe0\x7f')[0])
        self.assertTrue(val.string == '.z')

    def test_missing_value_conversion(self):
        columns = ['int8_', 'int16_', 'int32_', 'float32_', 'float64_']
        smv = StataMissingValue(101)
        keys = [key for key in iterkeys(smv.MISSING_VALUES)]
        keys.sort()
        data = []
        for i in range(27):
            row = [StataMissingValue(keys[i+(j*27)]) for j in range(5)]
            data.append(row)
        expected = DataFrame(data,columns=columns)

        parsed_113 = read_stata(self.dta17_113, convert_missing=True)
        parsed_115 = read_stata(self.dta17_115, convert_missing=True)
        parsed_117 = read_stata(self.dta17_117, convert_missing=True)

        tm.assert_frame_equal(expected, parsed_113)
        tm.assert_frame_equal(expected, parsed_115)
        tm.assert_frame_equal(expected, parsed_117)

    def test_big_dates(self):
        yr = [1960, 2000, 9999, 100, 2262, 1677]
        mo = [1, 1, 12, 1, 4, 9]
        dd = [1, 1, 31, 1, 22, 23]
        hr = [0, 0, 23, 0, 0, 0]
        mm = [0, 0, 59, 0, 0, 0]
        ss = [0, 0, 59, 0, 0, 0]
        expected = []
        for i in range(len(yr)):
            row = []
            for j in range(7):
                if j == 0:
                    row.append(
                        datetime(yr[i], mo[i], dd[i], hr[i], mm[i], ss[i]))
                elif j == 6:
                    row.append(datetime(yr[i], 1, 1))
                else:
                    row.append(datetime(yr[i], mo[i], dd[i]))
            expected.append(row)
        expected.append([NaT] * 7)
        columns = ['date_tc', 'date_td', 'date_tw', 'date_tm', 'date_tq',
                   'date_th', 'date_ty']
        # Fixes for weekly, quarterly,half,year
        expected[2][2] = datetime(9999,12,24)
        expected[2][3] = datetime(9999,12,1)
        expected[2][4] = datetime(9999,10,1)
        expected[2][5] = datetime(9999,7,1)
        expected[4][2] = datetime(2262,4,16)
        expected[4][3] = expected[4][4] = datetime(2262,4,1)
        expected[4][5] = expected[4][6] = datetime(2262,1,1)
        expected[5][2] = expected[5][3] = expected[5][4] = datetime(1677,10,1)
        expected[5][5] = expected[5][6] = datetime(1678,1,1)

        expected = DataFrame(expected, columns=columns, dtype=np.object)

        parsed_115 = read_stata(self.dta18_115)
        parsed_117 = read_stata(self.dta18_117)
        tm.assert_frame_equal(expected, parsed_115)
        tm.assert_frame_equal(expected, parsed_117)

        date_conversion =  dict((c, c[-2:]) for c in columns)
        #{c : c[-2:] for c in columns}
        with tm.ensure_clean() as path:
            expected.index.name = 'index'
            expected.to_stata(path, date_conversion)
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'),
                                  expected)

    def test_dtype_conversion(self):
        expected = self.read_csv(self.csv15)
        expected['byte_'] = expected['byte_'].astype(np.int8)
        expected['int_'] = expected['int_'].astype(np.int16)
        expected['long_'] = expected['long_'].astype(np.int32)
        expected['float_'] = expected['float_'].astype(np.float32)
        expected['double_'] = expected['double_'].astype(np.float64)
        expected['date_td'] = expected['date_td'].apply(datetime.strptime,
                                                        args=('%Y-%m-%d',))

        no_conversion = read_stata(self.dta15_117,
                                   convert_dates=True)
        tm.assert_frame_equal(expected, no_conversion)

        conversion = read_stata(self.dta15_117,
                                convert_dates=True,
                                preserve_dtypes=False)

        # read_csv types are the same
        expected = self.read_csv(self.csv15)
        expected['date_td'] = expected['date_td'].apply(datetime.strptime,
                                                        args=('%Y-%m-%d',))

        tm.assert_frame_equal(expected, conversion)

    def test_drop_column(self):
        expected = self.read_csv(self.csv15)
        expected['byte_'] = expected['byte_'].astype(np.int8)
        expected['int_'] = expected['int_'].astype(np.int16)
        expected['long_'] = expected['long_'].astype(np.int32)
        expected['float_'] = expected['float_'].astype(np.float32)
        expected['double_'] = expected['double_'].astype(np.float64)
        expected['date_td'] = expected['date_td'].apply(datetime.strptime,
                                                        args=('%Y-%m-%d',))

        columns = ['byte_', 'int_', 'long_']
        expected = expected[columns]
        dropped = read_stata(self.dta15_117, convert_dates=True,
                             columns=columns)

        tm.assert_frame_equal(expected, dropped)
        with tm.assertRaises(ValueError):
            columns = ['byte_', 'byte_']
            read_stata(self.dta15_117, convert_dates=True, columns=columns)

        with tm.assertRaises(ValueError):
            columns = ['byte_', 'int_', 'long_', 'not_found']
            read_stata(self.dta15_117, convert_dates=True, columns=columns)

    def test_categorical_writing(self):
        original = DataFrame.from_records(
            [
                ["one", "ten", "one", "one", "one", 1],
                ["two", "nine", "two", "two", "two", 2],
                ["three", "eight", "three", "three", "three", 3],
                ["four", "seven", 4, "four", "four", 4],
                ["five", "six", 5, np.nan, "five", 5],
                ["six", "five", 6, np.nan, "six", 6],
                ["seven", "four", 7, np.nan, "seven", 7],
                ["eight", "three", 8, np.nan, "eight", 8],
                ["nine", "two", 9, np.nan, "nine", 9],
                ["ten", "one", "ten", np.nan, "ten", 10]
            ],
            columns=['fully_labeled', 'fully_labeled2', 'incompletely_labeled',
                     'labeled_with_missings', 'float_labelled', 'unlabeled'])
        expected = original.copy()

        # these are all categoricals
        original = pd.concat([original[col].astype('category') for col in original], axis=1)

        expected['incompletely_labeled'] = expected['incompletely_labeled'].apply(str)
        expected['unlabeled'] = expected['unlabeled'].apply(str)
        expected = pd.concat([expected[col].astype('category') for col in expected], axis=1)
        expected.index.name = 'index'

        with tm.ensure_clean() as path:
            with warnings.catch_warnings(record=True) as w:
                # Silence warnings
                original.to_stata(path)
                written_and_read_again = self.read_dta(path)
                tm.assert_frame_equal(written_and_read_again.set_index('index'), expected)


    def test_categorical_warnings_and_errors(self):
        # Warning for non-string labels
        # Error for labels too long
        original = pd.DataFrame.from_records(
            [['a' * 10000],
             ['b' * 10000],
             ['c' * 10000],
             ['d' * 10000]],
            columns=['Too_long'])

        original = pd.concat([original[col].astype('category') for col in original], axis=1)
        with tm.ensure_clean() as path:
            tm.assertRaises(ValueError, original.to_stata, path)

        original = pd.DataFrame.from_records(
            [['a'],
             ['b'],
             ['c'],
             ['d'],
             [1]],
            columns=['Too_long'])
        original = pd.concat([original[col].astype('category') for col in original], axis=1)

        with warnings.catch_warnings(record=True) as w:
            original.to_stata(path)
            tm.assert_equal(len(w), 1)  # should get a warning for mixed content

    def test_categorical_with_stata_missing_values(self):
        values = [['a' + str(i)] for i in range(120)]
        values.append([np.nan])
        original = pd.DataFrame.from_records(values, columns=['many_labels'])
        original = pd.concat([original[col].astype('category') for col in original], axis=1)
        original.index.name = 'index'
        with tm.ensure_clean() as path:
            original.to_stata(path)
            written_and_read_again = self.read_dta(path)
            tm.assert_frame_equal(written_and_read_again.set_index('index'), original)

if __name__ == '__main__':
    nose.runmodule(argv=[__file__, '-vvs', '-x', '--pdb', '--pdb-failure'],
                   exit=False)

