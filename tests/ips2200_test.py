import unittest
import ips2200 as ips


class TestIps2200(unittest.TestCase):

    def test_callable(self):
        ref = ips.Ips2200()
        self.assertTrue(ref != None)


if __name__ == '__main__':
    unittest.main()
