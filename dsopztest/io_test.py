import unittest
import gzip
from dsopz import io
from dsopz import util

class ReaderWriterTest(unittest.TestCase):

    def setUp(self):
        util.makedirs('target/sandbox')

    def test_stream_plain(self):
        with io.jwriter(plain='target/sandbox/data.txt') as f:
            f.write('line1')
            f.write('line2')
        with io.jwriter(plain='target/sandbox/data.txt', append=True) as f:
            f.write('line3')
        with io.jreader(plain='target/sandbox/data.txt') as f:
            lines = [l for l in f]
            self.assertEqual(['line1', 'line2', 'line3'], lines)

    def test_stream_gz(self):
        with io.jwriter(gz='target/sandbox/data.txt.gz') as f:
            f.write('line1')
            f.write('line2')
        with io.jwriter(gz='target/sandbox/data.txt.gz', append=True) as f:
            f.write('line3')
        with io.jreader(gz='target/sandbox/data.txt.gz') as f:
            lines = [l for l in f]
            self.assertEqual(['line1', 'line2', 'line3'], lines)

if __name__ == '__main__':
    unittest.main()