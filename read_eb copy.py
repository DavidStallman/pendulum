import time
import u6
import curses
import atexit

from absl import app
from absl import flags

FLAGS = flags.FLAGS
flags.DEFINE_integer('addr', 0x36, 'Address of AS5600, 7 bit')
flags.DEFINE_boolean('burn_angle', False,
                    'Write zero and max angle setting to non-volatile storage.\n'
                    'WARNING: This can only be done 3 times.')
flags.DEFINE_boolean('clear', False,
                    'Clear the zero and max registers', short_name='c')
flags.DEFINE_boolean('monitor', False,
                     'Monitors')
flags.DEFINE_boolean('read', False,
                     'reads')
flags.DEFINE_boolean('zero_check', False,
                     'zero checks')
flags.DEFINE_boolean('zero_set', False,
                     'zero sets')


SCL_PIN_NUM = 0  # FIO0
SDA_PIN_NUM = 1  # FIO1

AS5600_ADDR = 0x36

class Encoder:

    def __init__(self) -> None:
        
        ljack = u6.U6()  # Opens first found U3 over USB

        if FLAGS.clear:
            print('Clearing')
            write_as5600_register(ljack, 0x01, 0)
            write_as5600_register(ljack, 0x02, 0)
            write_as5600_register(ljack, 0x03, 0)
            write_as5600_register(ljack, 0x04, 0)

        


    def read_as5600_registers(self, ljack):
        """ Read all readable registers.

        32 bytes read.
        Registers:
            0x00-0x88   - Config registers
            0x0C-0x0F   - Output registers
            0x0B        - Status Registers
            0x1A        - AGC
            0x1B-0x1C   - Magnitude (12 bit)

        args:
            ljack: open connection to a labjack

        Returns:
            List of 32 values
        """
        
        i2cbytes = [0 & 0xFF]
        ljack.i2c(AS5600_ADDR, i2cbytes, NumI2CBytesToReceive=0)
        ret = ljack.i2c(AS5600_ADDR, [], NumI2CBytesToReceive=32)
        i2cbytes = ret['I2CBytes']
        return i2cbytes


    def write_as5600_register(self, ljack, addr, data):
        """ Write one of the registers in the as5600.

        args:
            ljack: open connection to device
            addr: as5600 register address
            data: value to write to the specified register
        """
        i2cbytes = [addr & 0xFF, data & 0xFF]
        ljack.i2c(AS5600_ADDR, i2cbytes, NumI2CBytesToReceive=0)
        return

    def set_zero(self, ljack):
        registers = read_as5600_registers(ljack)
        write_as5600_register(ljack, 0x01, registers[0x0C])
        write_as5600_register(ljack, 0x02, registers[0x0D])

    def get_angle(self, ljack):
        return (registers[0x0E] & 0x0F)*256 + registers[0x0F]

    def cleanup(self, doit):
        """cleanup curses on exit."""
        if doit:
            curses.nocbreak()
            curses.echo()
            curses.endwin()

def main(argv):
    if len(argv) > 1:
        raise app.UsageError('Too many command line arguments.')
    
    ljack = u6.U6()  # Opens first found U3 over USB

    if FLAGS.clear:
        print('Clearing')
        write_as5600_register(ljack, 0x01, 0)
        write_as5600_register(ljack, 0x02, 0)
        write_as5600_register(ljack, 0x03, 0)
        write_as5600_register(ljack, 0x04, 0)
    
    if FLAGS.monitor:
        stdscr = curses.initscr()
        atexit.register(cleanup, True)
        curses.noecho()
        curses.cbreak()
        stdscr.nodelay(1)

        while True:
            stdscr.addstr(0, 0, 'Press any key stop.')
            stdscr.addstr(1, 0, 'Raw, Scaled')
            registers = read_as5600_registers(ljack)
            raw_angle = ((registers[0x0C] & 0X0F)*256) + registers[0x0D]
            scaled_angle = ((registers[0x0E] & 0X0F)*256) + registers[0x0F]
            output = f'{raw_angle:4d}, {scaled_angle:4d}'
            stdscr.addr(2, 0, output)

            c = stdscr.getch()
            if c != curses.ERR:
                break
        curses.nobreak()
        curses.echo()
        curses.endwin()
        atexit.register(cleanup, False)

    if FLAGS.read:
        registers = read_as5600_registers(ljack)
        print(f'Registers are {registers}')
        if (registers[0x0b] & 0x20) != 0x20:
            print('Magnet not present. \n')
        else:
            if (registers[0x0b] & 0x10) == 0x10:
                print('Magnet too Weak. \n')
            elif (registers[0x0b] & 0x08) == 0x08:
                print('Maget too strong.\n')
            print(f'AGC         = {registers[0x1A]:4d}')
            print('Magnitude    = {:4d}'.format(((registers[0x1B] & 0x0F)*256) + registers[0x1C]))
            print('Raw Angle    = {:4d}'.format(((registers[0x0C] & 0x0F)*256) + registers[0x0D]))
            print('Scaled Angle = {:4d}'.format(((registers[0x0E] & 0x0F)*256) + registers[0x0F]))
        print('PROGRAMMED   = {:4d} times'.format(registers[0x00] & 0x03))
        print('ZPOS         = {:4d}'.format(((registers[0x01] & 0x0F)*256) + registers[0x02]))
        print('MPOS         = {:4d}'.format(((registers[0x03] & 0x0F)*256) + registers[0x04]))
        print('MANG         = {:4d}'.format(((registers[0x05] & 0x0F)*256) + registers[0x06]))
        print('Config       = 0x{:4x}'.format(((registers[0x07] & 0x0F)*256) + registers[0x08]))

    if FLAGS.zero_check:
        registers = read_as5600_registers(ljack)
        raw_angle = ((registers[0x0C] & 0X0F)*256) + registers[0x0D]
        zero_pos = ((registers[0x01] & 0X0F)*256) + registers[0x02]
        print('Raw, zero, diff, status')
        print(f'{raw_angle:4d}, {zero_pos:4d}, {(raw_angle-zero_pos):4d}')

    if FLAGS.zero_set:
        registers = read_as5600_registers(ljack)
        write_as5600_register(ljack, 0x01, registers[0x0c])
        write_as5600_register(ljack, 0x02, registers[0x0d])

    ljack.close()

if __name__ == '__main__':
    print('running main')
    app.run(main)
