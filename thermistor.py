# main.py -- put your code here!


import pyb, math
from jtw import * 

setup();
#
#adc = pyb.ADC(pyb.Pin.board.X11)
#timer = pyb.Timer(1, freq=1)
#buf = bytearray(100)
#adc.read_timed(buf,tim)


def steinhart(thermistor_val):
    #steinhart b parameter 
    steinhart = math.log( thermistor_val / 10000) #10k @ 25c
    steinhart =  steinhart/3950 #beta coefficent 3000-4000
    steinhart = steinhart + 1/(25 + 273.15) #10k @ 25c and kelvin conversion respectively
    steinhart = 1/steinhart 
    steinhart = steinhart - 273.15 #convert back to C
    return steinhart
