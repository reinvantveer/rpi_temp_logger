#!/usr/bin/env python

import sqlite3
import os
import time
import glob
import json
import urllib2

# global variables
speriod=(15*60)-1
dbname='/var/www/templog.db'
local_weather_station = 'Utrecht,nl'

def get_local_temp():
    weather_url = 'http://api.openweathermap.org/data/2.5/weather?units=metric&q=' + local_weather_station
    jsondoc = urllib2.urlopen(weather_url).read()
    local_weather_dict = json.loads(jsondoc)
    local_temp = local_weather_dict['main']['temp']
    print 'Local temperature:', local_temp
    return local_temp

# store the temperature in the database
def log_temperature(temp):

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    curs.execute("INSERT INTO temps values(datetime('now', '+2 hours'), (?), (?))", (temp, get_local_temp()))

    # commit the changes
    conn.commit()

    conn.close()


# display the contents of the database
def display_data():

    conn=sqlite3.connect(dbname)
    curs=conn.cursor()

    for row in curs.execute("SELECT * FROM temps"):
        print str(row[0])+"	"+str(row[1])

    conn.close()



# get temerature
# returns None on error, or the temperature as a float
def get_temp(devicefile):

    try:
        fileobj = open(devicefile,'r')
        lines = fileobj.readlines()
        fileobj.close()
    except:
        return None

    # get the status from the end of line 1 
    status = lines[0][-4:-1]

    # is the status is ok, get the temperature from line 2
    if status=="YES":
        print status
        tempstr= lines[1][-6:-1]
        tempvalue=float(tempstr)/1000
        print tempvalue
        return tempvalue
    else:
        print "There was an error."
        return None

# main function: this is where the program starts 
def main():

    # enable kernel modules
    os.system('sudo modprobe w1-gpio')
    os.system('sudo modprobe w1-therm')

    # search for a device file that starts with 28
    devicelist = glob.glob('/sys/bus/w1/devices/28*')
    if devicelist=='':
        return None
    else:
        # append /w1slave to the device file
        w1devicefile = devicelist[0] + '/w1_slave'

#    while True:
    # get the temperature from the device file
    temperature = get_temp(w1devicefile)
    if temperature != None:
        print "temperature="+str(temperature)
    else:
        # Sometimes reads fail on the first attempt
        # so we need to retry
        temperature = get_temp(w1devicefile)
        print "temperature="+str(temperature)

        # Store the temperature in the database
    log_temperature(temperature)

    # display the contents of the database
	# display_data()
	# time.sleep(speriod)
    # get_local_temp()

if __name__=="__main__":
    main()




