#author: Sangay Lama
#version: 1.6
# Import DroneKit-Python
from dronekit import connect, VehicleMode, LocationGlobalRelative, LocationGlobal
import math
import time

# Connect to the Vehicle.
print("\nConnecting to vehicle on /dev/ttyACM0")
vehicle = connect('/dev/ttyACM0', wait_ready=True)

#a function for taking off
def arm_and_takeoff(aTargetAltitude):
    """
    Arms vehicle and fly to aTargetAltitude.
    """
    print("\nBasic pre-arm checks")
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print("Waiting for vehicle to initialise...")
        time.sleep(1)

    print("Arming motors")
    # Copter should arm in GUIDED mode
    vehicle.mode    = VehicleMode("GUIDED")
    vehicle.armed   = True

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:
        print("Waiting for arming...")
        time.sleep(1)

    print("Taking off!")
    vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

    # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command
    #  after Vehicle.simple_takeoff will execute immediately).
    while True:
        print("Altitude: "+ str(vehicle.location.global_relative_frame.alt))
        #Break and return from function just below target altitude.
        if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95:
            print("Reached target altitude")
            break
        time.sleep(1)

# a function to measure distance between two LocationGlobalRelative points
def get_distance_metres(aLocation1, aLocation2):
    """
    Returns the ground distance in metres between two LocationGlobal objects.

    This method is an approximation, and will not be accurate over large distances and close to the 
    earth's poles. It comes from the ArduPilot test code: 
    https://github.com/diydrones/ardupilot/blob/master/Tools/autotest/common.py
    """
    dlat = aLocation2.lat - aLocation1.lat
    dlong = aLocation2.lon - aLocation1.lon
    return math.sqrt((dlat*dlat) + (dlong*dlong)) * 1.113195e5



# Get some vehicle attributes (state)
print("\n\nCritical vehicle attribute values:")
print("GPS: %s" % vehicle.gps_0)
print("Battery: %s" % vehicle.battery)
print("Last Heartbeat: %s" % vehicle.last_heartbeat)
print("Is Armable?: %s" % vehicle.is_armable)
print("System status: %s" % vehicle.system_status.state)
print("Mode: %s" % vehicle.mode.name)    # settable
print("")
try:
	#prompting for confirmation so that the copter does not fly instantly on the running of this program
	action=str(raw_input("Do you want to start the flight? Enter y to continue. "))
	if action!='y':
		print ("Exitting...")
	else:
		print ("Continuing...")
		#getting the current location
		curr_location = vehicle.location.global_frame
		home = curr_location	#setting the location as home for later refernece.
		#setting up the destination location
		a_location = LocationGlobalRelative(27.608641,85.332669,20)

		# It is very important to check the distance before heading for any waypoints as the battery capacity is very limited.
		distance=get_distance_metres(curr_location, a_location)
		# Only Continue the mission if the distance to the destination is less than 100 metres.
		if distance >= 100:
			print("%s is too far." % a_location)
			print("The mission distance is greater than 100m i.e.%s Flight has been cancelled." % distance)
		else:

			print("The mission distance is "+ str(distance)+" metres.")

			#------------------------------------- Action Number : 1 ------------------------------------------------------
			#now, calling the arm and takeoff
			arm_and_takeoff(20)
			#--------------------------------------------------------------------------------------------------------------

			#------------------------------------- Action Number : 2 ------------------------------------------------------
			#Go to the target location, use simple goto until the distance from the target is at least 1m
			while distance >= 1:
				vehicle.simple_goto(a_location)
				curr_location = vehicle.location.global_frame
				distance=get_distance_metres(curr_location, a_location)
				time.sleep(4)
				print("FLying at height of "+ str(vehicle.location.global_frame.alt) +" metres.")
				print("--------The remaining distance is "+ str(distance)+ " metres.")
			#---------------------------------------------------------------------------------------------------------------

			#------------------------------------- Action Number : 3 -------------------------------------------------------
			#Loitering is like a position hold mode which holds its location and also listens for other inputs 
			#like remote commands, the below command will put the vehicle in loiter mode for 10 seconds
			vehicle.mode = VehicleMode("LOITER")
			print("...Loitering for 10 seconds...")
			time.sleep(5)
			#------------------------------------- Action Number : 4 -------------------------------------------------------
			# In the current working directory, there is a file named drop.py which triggers the drop.
			# Importing the file will drop the payload over the current location.			
			print("Dropping the package...")
			import drop
			time.sleep(5)
			print("\n.......................Drop Complete........................")
			#---------------------------------------------------------------------------------------------------------------

			#------------------------------------ Action Number : 5 --------------------------------------------------------
			# Now, the vehicle will return to its Launch Position, the motors are checked to be disarmed.
			vehicle.mode = VehicleMode("RTL")

			print("\nReturning to the Home now...")
			while (vehicle.armed):
				curr_location = vehicle.location.global_frame
				distance = get_distance_metres(curr_location, home)
				print("Distance to home : "+ str(distance) + " metres.")
				time.sleep(3)
			print("\n\n\n------------------Mission Complete ------------------")
	
except Exception as e:
	print(e)

