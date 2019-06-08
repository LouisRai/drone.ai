#author: Sangay Lama
#version: 1.2
from dronekit import connect, VehicleMode, LocationGlobalRelative
import time

# Connect to the Vehicle.
print"Connecting to vehicle on /dev/ttyACM0"
vehicle = connect('/dev/ttyACM0', wait_ready=True)

try: 
	while True:
		print"\nGetting Vehile Status..."
		time.sleep(1)
		print " GPS: %s" % vehicle.gps_0
		print " Battery: %s" % vehicle.battery
		print " Last Heartbeat: %s" % vehicle.last_heartbeat
		print " Is Armable?: %s" % vehicle.is_armable
		print " System status: %s" % vehicle.system_status.state
		print " Mode: %s" % vehicle.mode.name    # settable
		time.sleep(3)
except KeyboardInterrupt:
	print "The program was terminated."
