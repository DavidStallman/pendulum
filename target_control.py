from zaber_motion import Library
from zaber_motion.ascii import Connection
from zaber_motion import Units
import sys

# need to add the following udev rule to /etc/udev/rules.d/55-the-rules
# SUBSYSTEM=="TTY", ATTRS{idVendor}=="0403", ATTRS{idProduct}=="6001",
#   SYMLINK+="zaber", MODE:="0666"

max_distance = 1010 # max distance in CM
target_offset = 20 # cm from optical plane to target

def get_pos(axis):
  #return current position plus the offset
  curr_pos = axis.get_position(unit=Units.LENGTH_CENTIMETRES)
  corrected_pos = curr_pos + target_offset
  return corrected_pos

def main(argv):
  # Library.enable_device_deb_store()   # didn't work
  with Connection.open_serial_port('/dev/zaber') as connection:
    device_list = connection.detect_devices()
    device = device_list[0]  # grab the first one
    axis = device.get_axis(1)
    
    if argv[1] == 'read':
      print(f'Current position is {get_pos(axis)}')
    if argv[1] == 'home':
      axis.home()
    if argv[1] == 'abs':
      abs_pos = float(argv[2])
      if abs_pos > max_distance:
        print('Too far')
      else:
        axis.move_absolute(abs_pos, Units.LENGTH_CENTIMETRES)
    if argv[1] == 'rel':
      rel_pos = float(argv[2])
      axis.move_relative(rel_pos, Units.LENGTH_CENTIMETRES)
      # can also use Units.LENGTH_MILLIMETRES
      
if __name__ == '__main__':
  if len(sys.argv) > 3:
    print("Too argumentative")
    for arg in sys.argv:
      print(arg)
  elif len(sys.argv) == 1:
    print("""Available commands:
      read
      abs < distance in CM>
      rel < distance in CM>
      home"""
  else:
    if 'silent' not in sys.argv[1]:
      print('Welcome to the target mover')
    main(sys.argv)
          
