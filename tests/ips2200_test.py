import unittest
from ips2200 import I2CBuilder, print_value, to_address, from_address, to_memory, from_memory, split_bytes, join_bytes
import tests.fakes.busio as busio


# These values were found in the Programming Guide here:
#
#   https://www.renesas.com/us/en/document/gde/ips2200-programming-guide
#
# NOTE: The actual device stores addresses and values with extraneous bits
# according to the Programming Guide above. These are values that were hand
# transcribed from the documentation, and do not reflect the actual values
# found on the device. The actual values represent a transformation of these
# values.
doc_data = [
    # NVM Entries
    0x0323,  # 0x00 System Configuration 1
    0x0101,  # 0x01 System Configuration 2
    0x0056,  # 0x02 System Configuration 3
    0x0000,  # 0x03 Receiver 1/2 Gain
    0x0000,  # 0x04 System Configuration 3
    -1,  # 0x05 UNUSED?
    0x0000,  # 0x06 R1 Coil Offset
    0x00be,  # 0x07 Transmitter Current Calibration
    0x0000,  # 0x08 Transmitter Frequency Time Base Register Details
    0x0000,  # 0x09 Transmitter Lower Limit
    0x0000,  # 0x0a Transmitter Upper Limit
    0x0000,  # 0x0b Interrupt Enable 1
    0x0000,  # 0x0c Interrupt Enable 2
    0x0000,  # 0x0d IRQN Watchdog 1
    0x0000,  # 0x0e IRQN Watchdog 2
    -1,  # 0x0f UNUSED?

    -1,  # 0x10 UNUSED?
    -1,  # 0x11 UNUSED?
    0x0000,  # 0x12 R1 Fine Gain
    0x0000,  # 0x13 R2 Fine Gain
    -1,  # 0x14 UNUSED?
    -1,  # 0x15 UNUSED?
    -1,  # 0x16 UNUSED?
    -1,  # 0x17 UNUSED?
    -1,  # 0x18 UNUSED?
    -1,  # 0x19 UNUSED?
    -1,  # 0x1a UNUSED?
    -1,  # 0x1b UNUSED?
    -1,  # 0x1c UNUSED?
    -1,  # 0x1d UNUSED?
    -1,  # 0x1e UNUSED?
    -1,  # 0x1f UNUSED?

    # SRB Entries
    0x0323,  # 0x20 System Configuration 1
    0x0101,  # 0x21 System Configuration 2
    0x0056,  # 0x22 System Configuration 3
    0x0000,  # 0x23 Receiver 1/2 Gain
    0x0000,  # 0x24 System Configuration 3
    -1,  # 0x25 UNUSED?
    0x0000,  # 0x26 R1 Coil Offset
    0x00be,  # 0x27 Transmitter Current Calibration
    0x0000,  # 0x28 Transmitter Frequency Time Base Register Details
    0x0000,  # 0x29 Transmitter Lower Limit
    0x0000,  # 0x2a Transmitter Upper Limit
    0x0000,  # 0x2b Interrupt Enable 1
    0x0000,  # 0x2c Interrupt Enable 2
    0x0000,  # 0x2d IRQN Watchdog 1
    0x0000,  # 0x2e IRQN Watchdog 2
    -1,  # 0x2f UNUSED?

    -1,  # 0x30 UNUSED?
    -1,  # 0x31 UNUSED?
    0x0000,  # 0x32 R1 Fine Gain
    0x0000,  # 0x33 R2 Fine Gain

    # SFR Entries
    0x0000,  # 0x34 Interrupt Clear 1 (Write-only, read as 0)
    0x0000,  # 0x35 Interrupt Clear 2 (Write-only, read as 0)
    0x0000,  # 0x36 Interrupt State 1 (Read-only)
    0x0000,  # 0x37 Interrupt State 2 (Read-only)
    0x0000,  # 0x38 Transmitter Counter State
    -1,  # 0x39 UNUSED?
    0x0000,  # 0x3a NVM ECC Fail State
]


def generate_sim_data(data):
    # This function will create a sparse array that represents the data on the
    # device as it is retrieved and expected by a raw I2C interaction.
    result = [None] * 0xffff
    i = 0
    for entry in data:
        if (entry == -1):
            i += 1
            continue

        addr = 0
        if (i < 0x1f):
            # We're dealing with NVM entries
            addr = to_address(i, True)

        elif (i <= 0x3a):
            # We're dealing with SBR/SFR entries
            # try:
                addr = to_address(i, False)
            # except ValueError as err:
                # print_value('FAILED INDEX', i)



        value = split_bytes(to_memory(entry))
        result[addr] = value

        i += 1
        # print('------------')
        # print('addr: 0x' + format(addr, 'x'))
        # print('left: 0x' + format(value[0], 'x'))
        # print('right: 0x' + format(value[1], 'x'))

    return result



class TestIps2200Address(unittest.TestCase):
    # def test_to_address_raises(self):
        # with self.assertRaises(ValueError) as context:
            # to_address(0x33, False)
        # fragment = 'but was 0b110011'
        # self.assertIn(fragment, str(context.exception))

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


class TestIps2200Memory(unittest.TestCase):
    def test_to_memory_one(self):
        value = to_memory(0b111)
        self.assertEqual(value, 0xff)
        self.assertTrue(True)

    def test_from_memory_one(self):
        value = from_memory(0b11111111)
        self.assertEqual(value, 0b111)

    def test_split_bytes_dead(self):
        left, right = split_bytes(0xdead)
        self.assertEqual(left, 0xad)
        self.assertEqual(right, 0xde)

    def test_split_bytes_beef(self):
        left, right = split_bytes(0xbeef)
        self.assertEqual(left, 0xef)
        self.assertEqual(right, 0xbe)

    def test_join_bytes_dead(self):
        value = join_bytes(0xde, 0xad)
        self.assertEqual(value, 0xdead)

    def test_join_bytes_beef(self):
        value = join_bytes(0xbe, 0xef)
        self.assertEqual(value, 0xbeef)


class TestIps2200Data(unittest.TestCase):
    def test_generate_sim_data(self):
        d = generate_sim_data(doc_data)
        self.assertIsNotNone(d)
        value = d[0xc0]
        self.assertEqual(0x7f64, join_bytes(value[0], value[1]))
        value = d[0xc1]
        self.assertEqual(0x3f20, join_bytes(value[0], value[1]))
        value = d[0xc2]
        self.assertEqual(0xdf0a, join_bytes(value[0], value[1]))
        value = d[0xc3]
        self.assertEqual(0x1f00, join_bytes(value[0], value[1]))
        value = d[0xc7]
        self.assertEqual(0xdf17, join_bytes(value[0], value[1]))
        value = d[0xe0]
        self.assertEqual(0x7f64, join_bytes(value[0], value[1]))


class TestIps2200Builder(unittest.TestCase):
    def setUp(self):
        self.i2c = busio.I2C(generate_sim_data(doc_data))
        self.builder = I2CBuilder(0x18, self.i2c)

    def test_builder_is_instantiable(self):
        b = self.builder
        self.assertIsNotNone(b)

    def test_read_0x00(self):
        b = self.builder
        b.read_register(0x00)
        value = b.execute()
        self.assertEqual(value, 0x323)

    def test_read_0x20(self):
        b = self.builder
        b.use_nvm()
        b.read_register(0x00)
        value = b.execute()
        self.assertEqual(value, 0x323)

    def test_read_multiple(self):
        b = self.builder
        b.read_register(0x00)
        b.read_register(0x01)
        b.read_register(0x02)
        b.read_register(0x03)
        b.read_register(0x04)
        values = b.execute()
        self.assertEqual(values[0], 0x323)
        self.assertEqual(values[1], 0x0101)
        self.assertEqual(values[2], 0x0056)
        self.assertEqual(values[3], 0x0000)
        self.assertEqual(values[4], 0x0000)

    def test_write_0x00(self):
        b = self.builder
        b.write_register(0x00, 0x0327)
        b.execute()

        b.read_register(0x00)
        value = b.execute()
        self.assertEqual(value, 0x0327)


if __name__ == '__main__':
    unittest.main()
