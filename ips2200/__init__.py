
DEFAULT_DEVICE_ADDRESS = 0x18


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
        print('addr: 0x' + format(addr, 'x'))
        value = self._bus_read(bus, addr)
        print_value('existing:', value)
        print('bits: 0b' + format(bits, 'b'))
        bits = bits << start
        print('bits: 0b' + format(bits, 'b'))
        value = value ^ bits
        print_value('AFTER:', value)
        # print('mem_addr: 0x' + format(mem_addr, 'x'))
        bus.write(addr, value)

    def use_srb(self):
        # Turn off NVM flag
        self._use_nvm = False

    def use_nvm(self):
        # Turn on the NVM flag so that all address bits will have the NVM bit
        # flipped
        self._use_nvm = True
        return self

    def read_register(self, addr):
        # Read a register on the next call to execute
        self.operations.append(lambda bus: self._bus_read(bus, addr))

    def write_register(self, addr, value):
        # Write a register on the next call to execute
        self.operations.append(lambda bus: self._bus_write(bus, addr, value))

    def set_output_mode(self, mode):
        self.operations.append(lambda bus: self._write_bits_at(bus, 0x00, mode, 2, 3))

    def execute(self, bus=None):
        # Execute any stored operations
        if (bus is not None):
            self._bus = bus
        if (self._bus is None):
            raise ValueError('Cannot execute without first providing a bus')
        results = []
        for operation in self.operations:
            results.append(operation(self._bus))

        self.operations = []
        if (len(results) == 1):
            return results[0]

        return results

