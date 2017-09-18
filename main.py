from machine import I2C, Pin
import pyb, time

# global vars
tach0_cmd = bytes([0b00001100])
tach1_cmd = bytes([0b00001110])
config_cmd = bytes([0b00000010])
speed_cmd = bytes([0])
count_cmd = bytes([0b00010110])
gpio_cmd = bytes([0b00000100])
alarm_en_cmd = bytes([0b00001000])

# An object that handles macroscopic 6651 settings.
class Max6651(object):
    def read_reg(self, cmd):
        i2c.writeto(self.addr, cmd)
        return i2c.readfrom(self.addr, 1) 

    def __init__(self, addr_raw, full_on_raw, tach_overflow_raw):
        self.addr = addr_raw
        self.tach_count_time = 2 

        # Setup GPIO register: GPIO1 on the max6651 as FULL ON, GPIO 0 will be ALERT. Other GPIO will be logic high/ input
        gpio_reg = gpio_cmd + bytes([0b11110101])     
        i2c.writeto(self.addr, gpio_reg)

        # set tach overflow alert (GPIO 0 )
        alarm_reg = alarm_en_cmd + bytes([0b00000100])
        i2c.writeto(self.addr, alarm_reg)
        self.tach_overflow_pin = Pin(tach_overflow_raw, Pin.IN)

        # set pullup for full on operation 
        self.full_on_pin = Pin(full_on_raw, Pin.OUT)
        self.full_on_pin.value(1)

        # config register defaults to soft full-on, 12v fan, divide by 4 prescaler
        # calculate max rpm and prescale then set max6651 settings
        time.sleep_ms(5) # probably not needed. 
        self.max_rps = self.find_max_speed()
        self.tach_prescaler_bits = self.calc_prescale()
        config_val = 0b00101 #closed-loop operation, 12v fan operation
        config_val = ( config_val << 3) + self.tach_prescaler_bits
        config = config_cmd + bytes([config_val])    
        i2c.writeto(self.addr, config)
        # read for debug
        print(read_reg(config_cmd))


    def read_speed(self,tach_cmd):
        # fan speed value is between 0 -> 255, reusing equation on pg11 of datasheet
        # divide read value by tach_count_time. Experimentally I've found that to be accurate. 
        i2c.writeto(self.addr, tach_cmd)
        tach_max_raw = i2c.readfrom(self.addr, 1)  
        return ( int.from_bytes(tach_max_raw, 'big') / (2* self.tach_count_time) )

    def find_max_speed(self):
        self.full_on_pin.value(0) #full on low
        # set count time register at the slowest count time (2s or 3825rpm)
        count_time_reg = count_cmd + bytes([0b00000011])
        i2c.writeto(self.addr, count_time_reg)

        # TODO: Fix overflow handling 
        if self.tach_overflow_pin.value() == 1 :
            #decrement count time reg to next count time (1s or 7680rpm)
            self.tach_count_time = 1
            count_time_reg = count_cmd + bytes([0b00000010])
            i2c.writeto(self.addr, count_time_reg)

        # TODO: multi sampling just in case we read the reg at the wrong time?
        time.sleep_ms(40)
        fan0_rps = self.read_speed(tach0_cmd)
        self.full_on_pin.value(1)
        return fan0_rps

    def calc_prescale(self):
        # calculate ideal prescaler value for closed loop operation (target = 64)
        # equation 1 on pg 21 
        prescale_dict = {1 : 0b000 , 2 : 0b001 , 4 : 0b010 , 8 : 0b011 , 16 : 0b100}
        tach_prescaler_tmp = self.max_rps * 64 / 992 
        tach_prescaler = min(prescale_dict, key=lambda x:abs(x-tach_prescaler_tmp)) # find closest value
        # debug 
        #print('tach_prescaler:', tach_prescaler)
        #print("tach_prescaler_bits:",prescale_dict[tach_prescaler])
        return prescale_dict[tach_prescaler] # return 3 bit value

    def set_target_speed(self, target_percentage):
            tach_prescaler = 2**self.tach_prescaler_bits
            target_rps = (target_percentage / 100) * self.max_rps
            speed = round( (992 * tach_prescaler / target_rps) - 1 ) 
            print('tach_prescaler:', tach_prescaler)
            print('target:',  target_rps)
            print('calculated speed val:', speed)
            speed_word = speed_cmd + bytes([speed])
            i2c.writeto(self.addr, speed_word)
            assert self.read_reg(speed_cmd) == speed_word
                
# init i2c interface
scl = pyb.Pin.board.Y9
sda = pyb.Pin.board.Y10
i2c = I2C(-1,scl,sda,freq=200000)
# pin x1 connected to max6651 gpio1 for full_on operation,
# pin x2 connected to max6651 gpio 0 for tach count overflow
zone1 = Max6651(72, 'X1', 'X2')
print ( zone1.read_speed(tach0_cmd) )
#zone1.set_target_speed(50, 40)
#time.sleep_ms(50)
#print ( zone1.read_speed(tach0_cmd) )

