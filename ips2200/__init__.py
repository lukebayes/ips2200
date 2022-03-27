
DEFAULT_DEVICE_ADDRESS = 0x18


class Constants():
    # Register Base Addresses
    RegAddrSystemConfig1 = 0x00
    RegAddrSystemConfig2 = 0x01
    RegAddrR1R2Gain = 0x02
    RegAddrSystemConfig3 = 0x03
    RegAddrR2CoilOffset = 0x04
    RegAddrR1CoilOffset = 0x06
    RegAddrTXCurrentCalib = 0x07
    RegAddrTXFreqCalib = 0x08
    RegAddrTXFreqLowerLimit = 0x09
    RegAddrTXFreqUpperLimit = 0x0a
    RegAddrInterrupt1Enable = 0x0b
    RegAddrInterrupt2Enable = 0x0b
    RegAddrIRQNWatchdog1 = 0x0d
    RegAddrIRQNWatchdog2 = 0x0e

    SpiDataOrder = (RegAddrSystemConfig1, 10, 10)
    SpiDataOrderMsb = 0b0
    SpiDataOrderLsb = 0b1

    SpiMode = (RegAddrSystemConfig1, 8, 9)
    SpiModePhaseRisingFalling = 0b00
    SpiModePhaseFallingRising = 0b01
    SpiModePolarityRisingFalling = 0b10
    SpiModePolarityFallingRising = 0b11

    I2CAddress = (RegAddrSystemConfig1, 4, 7)

    OutputMode = (RegAddrSystemConfig1, 2, 3)
    OutputModeSinCosNN = 0b00
    OutputModeSinCosRef = 0b01
    OutputModeQuadABN = 0b10
    OutputModeQuadAB = 0b11

    SystemProtocol = (RegAddrSystemConfig1, 0, 1)
    SystemProtocolSpi = 0b00
    SystemProtocolSpiInterrupt = 0b01
    SystemProtocolI2CInterrupt = 0b10
    SystemProtocolI2CInterruptAddress = 0b11

    QuadModeXor = (RegAddrSystemConfig2, 10, 10)
    QuadModeOnePulse = 0b0
    QuadModeDoublePulse = 0b1


def print_value(label, value):
    print('-------------------')
    print(label, 'dec: 0d' + str(value))
    print(label, 'hex: 0x' + format(value, 'x'))
    print(label, 'bin: 0b' + format(value, 'b'))


def to_address(value, use_nvm):
    # Convert the documented address (e.g. 0x00 to the actual value that the
    # i2c device will accept (e.g., insert leading bits and configure the
    # address space bit.
    #
    # Memory addresses in the IPS2200 consume a number of bits to describe the
    # operation.
    #
    # Bits 0-4: 5 bit base memory address value
    # Bit 5: HIGH indicates SRB/SFR address type, LOW indicates NVM memory
    # Bit 6 & 7: Always HIGH
    # if (value > 0x32):
    #     raise ValueError('Provided value must only use first 5 bits (< 31), ' +
    #                      'but was 0b' + format(value, 'b') + ' instead. To ' +
    #                      'select between NVM and SRB/SFR, pass use_nvm=Bool ' +
    #                      'argument to this function.')
    if (use_nvm):
        # Bit 6 is low if using NVM
        return value | 0b11000000
    else:
        # Bit 6 is high if using NVM
        return value | 0b11100000


def from_address(value):
    # Convert from a provided actual i2c memory address into the documented
    # address by removing leading (unused) bits and separating the NVM/SBR
    # flag.
    #
    # Memory addresses in the IPS2200 consume a number of bits to describe the
    # operation.
    #
    # Bits 0-4: 5 bit base memory address value
    # Bit 5: HIGH indicates SRB/SFR address type, LOW indicates NVM memory
    # Bit 6 & 7: Always HIGH
    if (value > 0b11111111):
        raise ValueError('Provided value must not be larger than a single ' +
                         'byte but was 0b' + format(value, 'b') + ' instead.')
    return value ^ 0b11000000


def to_memory(value):
    # Left shift 5 bits onto the provided value and ensure bits 0-4 are 1
    return (value << 5) ^ 0b11111


def from_memory(value):
    # Right shift unused 5 bits from the right and return the value
    return value >> 5


def split_bytes(value):
    # Separate the provided double byte integer into 2 independent bytes.
    return [value & 0xff, value >> 8 & 0xff]


def join_bytes(left, right):
    # Join the provided single byte integers into a single double type value.
    return ((0xff & left) << 8) ^ right


class I2CBuilder():
    def __init__(self, device_address, bus=None):
        self._device_address = device_address
        self._use_nvm = False
        self._bus = bus
        self.operations = []

    def _bus_read(self, bus, addr):
        results = [0x00, 0x00]
        addr = to_address(addr, self._use_nvm)
        bus.write_readinto([self._device_address, addr], results)
        return from_memory(join_bytes(results[1], results[0]))

    def _bus_write(self, bus, addr, value):
        addr = to_address(addr, self._use_nvm)
        parts = split_bytes(to_memory(value))
        bus.write(addr, parts)

    def _write_bits_at(self, bus, addr, bits, start, end):
        value = self._bus_read(bus, addr)
        bits = bits << start
        value = value ^ bits
        self._bus_write(bus, addr, value)

    def _append_op(self, config, value):
        addr = config[0]
        start = config[1]
        end = config[2]
        self.operations.append(lambda bus: self._write_bits_at(bus, addr, value, start, end))

    def clear_operations(self):
        self.operations = []
        return self

    def use_srb(self):
        # Turn off NVM flag
        self._use_nvm = False
        return self

    def use_nvm(self):
        # Turn on the NVM flag so that all address bits will have the NVM bit
        # flipped
        self._use_nvm = True
        return self

    def read_register(self, addr):
        # Read a register on the next call to execute
        self.operations.append(lambda bus: self._bus_read(bus, addr))
        return self

    def write_register(self, addr, value):
        # Write a register on the next call to execute
        self.operations.append(lambda bus: self._bus_write(bus, addr, value))
        return self

    def set_output_mode(self, mode):
        self._append_op(Constants.OutputMode, mode)
        return self

    def set_spi_data_order(self, order):
        self._append_op(Constants.SpiDataOrder, order)
        return self

    def set_spi_mode(self, mode):
        self._append_op(Constants.SpiMode, mode)
        return self

    def set_i2c_address(self, addr):
        self._append_op(Constants.I2CAddress, addr)
        return self

    def set_system_protocol(self, protocol):
        self._append_op(Constants.SystemProtocol, protocol)
        return self

    def set_quad_mode_xor(self, value):
        self._append_op(Constants.QuadModeXor, value)
        return self

    def execute(self, bus=None):
        # Execute any stored operations
        if (bus is not None):
            self._bus = bus
        if (self._bus is None):
            raise ValueError('Cannot execute without first providing a bus')
        results = []
        for operation in self.operations:
            result = operation(self._bus)
            if (result is not None):
                results.append(result)

        self.clear_operations()
        result_count = len(results)
        if (result_count == 0):
            return None
        elif (result_count == 1):
            return results[0]
        else:
            return results

