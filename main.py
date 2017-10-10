import fan_control, time
from machine import I2C
from thermistor import read_temp
# init i2c interface
scl = pyb.Pin.board.Y9
sda = pyb.Pin.board.Y10
i2c = I2C(-1,scl,sda,freq=200000)
# pin x1 connected to max6651 gpio1 for full_on operation,
# pin x2 connected to max6651 gpio0 for tach count overflow
zone1 = fan_control.Max6651(72, i2c, 'X1', 'X2')

# init ADC
ambient_sensor= pyb.ADC(pyb.Pin.board.X12)
loop_sensor= pyb.ADC(pyb.Pin.board.X11)

while(1):
    loop_temp = read_temp(loop_sensor)
    ambient_temp = read_temp(ambient_sensor)

    print('Loop Temperature: ', loop_temp)
    print('Ambient Temperature: ', ambient_temp)
    print('Delta T:', loop_temp - ambient_temp) 
    time.sleep(10)

    
