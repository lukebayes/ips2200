
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
    if (value > 0b11111):
        raise ValueError('Provided value must only use first 5 bits (< 31), ' +
                         'but was 0b' + format(value, 'b') + ' instead. To ' +
                         'select between NVM and SRB/SFR, pass use_nvm=Bool ' +
                         'argument to this function.')

    print("use_nvm:", use_nvm, "value:", value, format(value, 'b'))
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
    pass


def from_memory(value):
    pass


class I2CBuilder():
    def __init__(self, device_addr=DEFAULT_DEVICE_ADDRESS):
        self._use_nvm = False
        self._cache = {}
        self._device_addr = device_addr
        self.operations = []

    def use_nvm(self):
        self._use_nvm = True
        return self

    def _bus_read(self, bus, addr):
        return bus.read(to_address(addr, self._use_nvm))

    def _bus_write(self, bus, addr, value):
        return bus.write(to_address(addr, self._use_nvm), value)

    def _get_value_at(self, bus, addr):
        if (self._cache[addr] is None):
            self._cache[addr] = self._bus_read(addr)

        return self._cache[addr]

    def _set_value_at(self, bus, addr, indices, bits):
        value = self._get_value_at(bus, addr)

    def set_register(self, addr, indices, bits):
        self.operations.append(lambda bus: self._set_value_at(bus, addr,
                                                              indices, bits))
        return self


class I2CBusWrapper():
    def __init__(self, delegate, dev_addr, use_nvm):
        self._dev_addr = dev_addr
        self._delegate = delegate
        self._use_nvm = use_nvm

    def write(self, mem_addr, value):
        addr = to_address(mem_addr, self._use_nvm)
        return delegate.write(self._dev_addr, addr, value)

    def read(self, mem_addr):
        addr = to_address(mem_addr, self._use_nvm)
        return delegate.read(self._dev_addr, addr)


class Ips2200():
    # The IPS2200 class provides a semantic interface to the device i2c API.

    def __init__(self, use_nvm=False, bus=None):
        self._bus = bus
        self.use_nvm = use_nvm
