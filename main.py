import time
import pyb
#import fan_control
#from machine import I2C
from thermistor import read_temp

# init i2c interface
#scl = pyb.Pin.board.Y9
#sda = pyb.Pin.board.Y10
#i2c = I2C(-1,scl,sda,freq=200000)

# pin x1 -> max6651 gpio1 for full_on operation,
# pin x2 -> max6651 gpio0 for tach count overflow
#zone1 = fan_control.Max6651(72, i2c, 'X1', 'X2')

# init USB comm
usb = pyb.USB_VCP()
#usb.setinterrupt(-1)  # disable keyboard int
#assert usb.isconnected()

# define thermistors
loop_sensor = pyb.ADC(pyb.Pin.board.X11)
ambient_sensor = pyb.ADC(pyb.Pin.board.X12)

def cmd_switch(cmd):
    if cmd == "T?=AMB": # query ambient temp
        ambient_temp = read_temp(ambient_sensor)
        #print(ambient_temp)
        usb.write(ambient_temp)
    elif cmd ==  "T?=LOP": # query loop temp
        loop_temp = read_temp(loop_sensor)
        usb.write(loop_temp)
    else:
        print("ERROR")
        return -1

while(1):
    # poll usb commands
    usb_buf = usb.read()
    if usb_buf is not None:
        #print(usb_buf.decode())
        cmd_switch(usb_buf.decode().rstrip())

    time.sleep(3)
