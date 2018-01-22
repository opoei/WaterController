import wmi
import serial
import json

# Using OHM was the cleanest way of obtaining sensor information.
# Creating a C extension would remove the dependency, but is
# significantly more complex.
# I did try a few pure python libraries, none of which works on
# windoze.

sensors = wmi.WMI(namespace="root\OpenHardwareMonitor").Sensor()
for sensor in sensors:
    if sensor.SensorType == 'Temperature':
        if sensor.Name.startswith("CPU Core"):
            print(sensor.Name, "Temp")
            print(sensor.Value)
        elif sensor.Name == 'GPU Core':
            print(sensor.Name, "Temp")
            print(sensor.Value)
    if sensor.SensorType == 'Load':
        if sensor.Name.startswith('CPU Core'):
            print(sensor.Name, "Load")
            print(sensor.Value)
        elif sensor.Name == 'GPU Core':
            print(sensor.Name, "Load")
            print(sensor.Value)

# Scan com ports
wmiObj = wmi.WMI()
pnpEntries = wmiObj.query("SELECT * FROM  Win32_PnPEntity")
for entry in pnpEntries:
    if entry.Description.startswith('Pyboard USB'):
        idx = entry.Name.rindex('COM')
        comPort = entry.Name[idx:(idx + 4)]

ser = serial.Serial(port=comPort, baudrate=115200)
ser_data = {'cmd': 'AMB'}
ser.write(json.dumps(ser_data))
print(ser.readline().decode())
ser.close()
