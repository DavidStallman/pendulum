import read_eb
from zaber_motion import Units
from zaber_motion.ascii import Connection
import time




encoder = read_eb.Encoder()
print(encoder.get_angle())
print('Zeroing')
encoder.set_zero()
print(f'Angle is now {encoder.get_angle()}')

with Connection.open_serial_port("COM3") as connection:
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    device = device_list[0]

    axis = device.get_axis(1)
    axis.home()
    print(f'Current location is {axis.get_position()}')
    # if not axis.is_homed():
    #   axis.home()

    # Move to 10mm
    starting_point = 500
    axis.move_absolute(starting_point, Units.LENGTH_MILLIMETRES)

    current_location = axis.get_position()

    time.sleep(2)

    p = 1.4         # worked well 1.4, slow drift
    i = 0.001
    d = .11
    target_angle = 2020
    target_position = 1

    last_angle = 0
    print('Starting')

    max_pos = 100000
    min_pos = 0000
    
    while True:
        
        current_angle = encoder.get_angle()
        error = target_angle - current_angle
        relative_move = error*p + d*(last_angle-current_angle)
        print(f'relative move {relative_move}, from {current_location}')
        if (current_location + relative_move) > max_pos:
            axis.move_absolute(starting_point, Units.LENGTH_MILLIMETRES)
            current_location = axis.get_position()
        elif (current_location + relative_move) < min_pos:
            axis.move_absolute(starting_point, Units.LENGTH_MILLIMETRES)
            current_location = axis.get_position()
        else:
            print(f'Moving {relative_move}')
            axis.move_relative(relative_move, Units.LENGTH_MILLIMETRES, wait_until_idle=False)
            last_angle = current_angle
            current_location = current_location + relative_move

