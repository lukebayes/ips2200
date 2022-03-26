
class I2C():

    def __init__(self, cache=None):
        self._cache = cache

    def write_readinto(self, out_buffer, in_buffer):
        # For IPS2200 I2C, the out_buffer has 2 entries [dev addr, mem addr].
        # The in_buffer has 2 entries, which are both bytes from storage being
        # read from the provided address.
        index = out_buffer[1]

        # NOTE: Was storing double byte integers, but trying out storing bytes
        # separately to more closely match what I'm seeing come out of the
        # actual device.
        # left = parts >> 8
        # right = parts & 0xff
        # in_buffer[0] = left
        # in_buffer[1] = right
        values = self._cache[index]
        in_buffer[0] = values[0]
        in_buffer[1] = values[1]

    def write(self, addr, value):
        self._cache[addr] = value
