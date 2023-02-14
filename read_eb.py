


import time
import u6

dev = u6.U6()  # Opens first found U3 over USB

SCL_PIN_NUM = 0  # FIO0
SDA_PIN_NUM = 1  # FIO1

AS5600_ADDR = 0x36

def read_as5600_registers(ljack):
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


def write_as5600_register(ljack, addr, data):
    """ Write one of the registers in the as5600.

    args:
        ljack: open connection to device
        addr: as5600 register address
        data: value to write to the specified register
    """
    i2cbytes = [addr & 0xFF, data & 0xFF]
    ljack.i2c(AS5600_ADDR, i2cbytes, NumI2CBytesToReceive=0)
    return

def set_zero(ljack):
    registers = read_as5600_registers(ljack)
    write_as5600_register(ljack, 0x01, registers[0x0C])
    write_as5600_register(ljack, 0x02, registers[0x0D])

def get_angle(ljack):
    return (registers[0x0E] & 0x0F)*256 + registers[0x0F]


registers = read_as5600_registers(dev)

print(f'Raw Angle: {(registers[0x0E] & 0x0F)*256+registers[0x0F]:4d}')

print('setting zero')

set_zero(dev)

registers = read_as5600_registers(dev)

print(f' Angle: {(registers[0x0E] & 0x0F)*256+registers[0x0F]:4d}')

print(f'Will time how long it takes to read 100 times')
start_time = time.perf_counter()

for i in range(100):
    get_angle(dev) 
end_time = time.perf_counter()
elapsed_time = end_time - start_time
print(f'That took {elapsed_time}, or {elapsed_time/100} per call')

