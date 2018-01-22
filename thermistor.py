import pyb
import math

def read_temp(sensor):
    def steinhart(thermistor_val):
        #steinhart b parameter
        steinhart = math.log( thermistor_val / 10000) #10k @ 25c
        steinhart =  steinhart/3950 #beta coefficent 3000-4000
        steinhart = steinhart + 1/(25 + 273.15) #10k @ 25c and kelvin conversion respectively
        steinhart = 1/steinhart
        steinhart = steinhart - 273.15 #convert back to C
        return steinhart

    adc = sensor.read()
    val = 10000 * adc / (4095 - adc )
    return steinhart(val)

