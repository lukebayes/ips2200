import unittest
from .fakes import busio

fake_data = [
    # NVM Entries
    [0x23, 0x03],  # 0x00 System Configuration 1
    [0x01, 0x01],  # 0x01 System Configuration 2
    [0x56, 0x00],  # 0x02 System Configuration 3
    [0x00, 0x00],  # 0x03 Receiver 1/2 Gain
    [0x00, 0x00],  # 0x04 System Configuration 3
]


class TestFakeBusio(unittest.TestCase):
    def test_busio_callable(self):
        b = busio.I2C()
        self.assertIsNotNone(b)

    def test_busio_cache(self):
        b = busio.I2C(fake_data)
        bufout = [0x18, 0x02]
        bufin = [0x00, 0x00]
        b.write_readinto(bufout, bufin)
        self.assertEqual(bufin[0], 0x56)
        self.assertEqual(bufin[1], 0x00)


if __name__ == '__main__':
    unittest.main()
