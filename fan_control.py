from machine import I2C, Pin
import pyb, time

#TODO: Add failsafes for fan speed
#TODO: Cleanup print statements, and write in asserts.

# global vars
tach0_cmd = bytes([0b00001100])
tach1_cmd = bytes([0b00001110])
config_cmd = bytes([0b00000010])
speed_cmd = bytes([0])
count_cmd = bytes([0b00010110])
gpio_cmd = bytes([0b00000100])
alarm_en_cmd = bytes([0b00001000])

# An class that handles macroscopic MAX6651 operations.
class Max6651(object):

    def __init__(self, addr_raw, i2c, full_on_extern, tach_overflow_extern):
        self.i2c = i2c 
        self.addr = addr_raw
        self.tach_count_time = 2 

        # Setup GPIO register: GPIO 0 will be ALERT. Other GPIO will be logic high/ input
        # GPIO 1 will be set as full on, with the intention of acting as a fail safe for
        #   microcontroller failure. DO NOT PULL LOW DURING NORMAL OPERATION. It requires
        #   resetting config register after doing so. Currently do not have a routine to 
        #   handle reading, saving, and re-setting the config register. Dont really see a
        #   need for it.
        gpio_reg = gpio_cmd + bytes([0b11110101])     
        self.i2c.writeto(self.addr, gpio_reg)

        # set tach overflow alert (GPIO 0 )
        alarm_reg = alarm_en_cmd + bytes([0b00000100])
        self.i2c.writeto(self.addr, alarm_reg)
        self.tach_overflow_pin = Pin(tach_overflow_extern, Pin.IN)

        # set pullup for full on operation 
        self.full_on_pin = Pin(full_on_extern, Pin.OUT)
        self.full_on_pin.on()

        # config register defaults to soft full-on, 12v fan, divide by 4 prescaler
        # calculate max rpm and prescale, then set max6651 settings
        time.sleep_ms(5) # probably not needed. 
        self.max_rps = self.find_max_speed()
        self.tach_prescaler_bits = self.calc_prescale()
        config_val = 0b00101 #closed-loop operation, 12v fan operation
        config_val = ( config_val << 3) + self.tach_prescaler_bits
        config = config_cmd + bytes([config_val])    
        self.i2c.writeto(self.addr, config)
        # debug
        config_reg_read = int.from_bytes(self.read_reg(config_cmd), 'big')
        #assert self.read_reg(config_cmd) == config
        print("config int:", config_reg_read, '\n')
        print("config binary:", bin(config_reg_read), '\n')
        print("config raw:", int.from_bytes(config, 'big'), '\n')

    def read_reg(self, cmd):
        self.i2c.writeto(self.addr, cmd)
        return self.i2c.readfrom(self.addr, 1) 

    def read_speed(self,tach_cmd):
        # fan speed value is between 0 -> 255, reusing equation on pg11 of datasheet
        self.i2c.writeto(self.addr, tach_cmd)
        tach_max_raw = self.i2c.readfrom(self.addr, 1)  
        return ( int.from_bytes(tach_max_raw, 'big') / (2* self.tach_count_time) )

    def find_max_speed(self):
        #following the datasheet reccomendation of full off -> full on -> closed loop
        # set soft fan off. other values are default config reg
        config = config_cmd + bytes([0b00011010])
        self.i2c.writeto(self.addr, config)
        # set soft full on. other values are default config reg
        config = config_cmd + bytes([0b00001010])
        self.i2c.writeto(self.addr, config)

        # set count time register at the slowest count time (2s or 3825rpm)
        count_time_reg = count_cmd + bytes([0b00000011])
        self.i2c.writeto(self.addr, count_time_reg)

        # TODO: Fix overflow handling 
        if self.tach_overflow_pin.value() == 1 :
            #decrement count time reg to next count time (1s or 7680rpm)
            self.tach_count_time = 1
            count_time_reg = count_cmd + bytes([0b00000010])
            self.i2c.writeto(self.addr, count_time_reg)

        # Verifying we are at max speed. sample every half a second for 2 seconds.
        # Block until fan is spinning. 
        # REVIEW: No idea how this interacts with fans faster than 3825rpm,
        #           it also desperately needs some form of an algorithim...
        tach0_sample = self.read_speed(tach0_cmd)
        while tach0_sample < 1:
            time.sleep_ms(50)
            tach0_sample = self.read_speed(tach0_cmd)
        itr = 0
        while itr < 3: 
            time.sleep(0.5)
            tach0_sample_2 = self.read_speed(tach0_cmd)
            if tach0_sample == tach0_sample_2:
                tach0_sample = tach0_sample_2 
                itr += 1
            else:
                itr = 0
        return tach0_sample

    def calc_prescale(self):
        # calculate ideal prescaler value for closed loop operation (target = 64)
        # equation 1 on pg 21 
        prescale_dict = {1 : 0b000 , 2 : 0b001 , 4 : 0b010 , 8 : 0b011 , 16 : 0b100}
        tach_prescaler_tmp = self.max_rps * 64 / 992 
        tach_prescaler = min(prescale_dict, key=lambda x:abs(x-tach_prescaler_tmp)) # find closest value
        # debug 
        print('tach_prescaler:', tach_prescaler)
        print("tach_prescaler_bits:",prescale_dict[tach_prescaler])
        return prescale_dict[tach_prescaler] # return 3 bit value

    def set_target_speed(self, target_percentage):
            tach_prescaler = 2**self.tach_prescaler_bits
            target_rps = (target_percentage / 100) * self.max_rps
            speed = round( (992 * tach_prescaler / target_rps) - 1 ) 
            print('tach_prescaler:', tach_prescaler)
            print('target:',  target_rps)
            print('calculated speed val:', speed)
            speed_word = speed_cmd + bytes([speed])
            self.i2c.writeto(self.addr, speed_word)
            assert self.read_reg(speed_cmd) == bytes([speed])
                

