import re
import unittest
from ips2200 import *

# print('value:', '0x' + format(value, 'x'))

class FakeBus():
    def __init__(self):
        self._cache = {}

    def write(self, dev_addr, mem_addr, value):
        self._cache[mem_addr] = value


    def read(self, dev_addr, mem_addr):
        if (self._cache[mem_addr] is None):
            raise Exception('Cannot read from unconfigured memory address')

        return self._cache[mem_addr]

class TestFakeBus(unittest.TestCase):

    def test_callable(self):
        fb = FakeBus()
        self.assertIsNotNone(fb)


class TestIps2200(unittest.TestCase):

    def test_callable(self):
        ref = Ips2200()
        self.assertTrue(ref != None)

    def test_to_address_raises(self):
        with self.assertRaises(ValueError) as context:
            to_address(0x20, False)
        fragment = 'but was 0b100000'
        self.assertIn(fragment, str(context.exception))

    def test_to_sbr_address_with_sys1(self):
        value = to_address(0x00, False)
        self.assertEqual(value, 0xe0)

    def test_to_nvm_address_with_sys1(self):
        value = to_address(0x00, True)
        self.assertEqual(value, 0xc0)

    def test_to_sbr_address_with_sys3(self):
        value = to_address(0x03, False)
        self.assertEqual(value, 0xe3)

    def test_to_nvm_address_with_sys3(self):
        value = to_address(0x03, True)
        self.assertEqual(value, 0xc3)

    def test_from_address_raises(self):
        with self.assertRaises(ValueError) as context:
            from_address(0xff1)
        fragment = 'but was 0b111111110001'
        self.assertIn(fragment, str(context.exception))

    def test_from_sbr_address_with_sys1(self):
        value = from_address(0xe0)
        self.assertEqual(value, 0x20)

    def test_from_nvm_address_with_sys1(self):
        value = from_address(0xc0)
        self.assertEqual(value, 0x0)

    def test_from_sbr_address_with_sys3(self):
        value = from_address(0xe3)
        self.assertEqual(value, 0x23)

    def test_from_nvm_address_with_sys3(self):
        value = from_address(0xc3)
        self.assertEqual(value, 0x03)

    def test_builder_is_instantiable(self):
        b = I2CBuilder()
        self.assertIsNotNone(b)

    def test_builder_use_nvm(self):
        b = I2CBuilder().use_nvm()
        self.assertIsNotNone(b)

    def test_builder_set_register(self):
        b = I2CBuilder().set_register(0x00, 10, 0b1)
        operation = b.operations[0]
        self.assertIsNotNone(operation)

        fake_bus = FakeBus()
        fake_bus.write(0x18, to_address(0x00, False), 0x323)
        # value = operation(fake_bus)


if __name__ == '__main__':
    unittest.main()
