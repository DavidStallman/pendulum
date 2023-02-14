from zaber_motion import Units
from zaber_motion.ascii import Connection

with Connection.open_serial_port("COM3") as connection:
    device_list = connection.detect_devices()
    print("Found {} devices".format(len(device_list)))

    device = device_list[0]

    axis = device.get_axis(1)
    if not axis.is_homed():
      axis.home()

    # Move to 10mm
    axis.move_absolute(10, Units.LENGTH_MILLIMETRES)

    # Move by an additional 5mm
    axis.move_relative(5, Units.LENGTH_MILLIMETRES)
