#! /usr/bin/env python3
# author: Jake Mowatt

from json import loads  # steps 3, 4
from requests import get  # steps 3, 4
from socket import gethostbyname  # step 1
from subprocess import getstatusoutput  # step 2
from sys import argv  # command line arguments
import matplotlib.pyplot as plt #for temp plotting function
import numpy as np #for temp plotting function

# Takes an array of temps
# and plots them.
def plot_temps(temps):
    xs = [x for x in range(len(temps))]
    plt.plot(xs, temps, label="Hourly tempatures")

    #Label the x and y
    plt.xlabel("Hour")
    plt.ylabel("Temperature F.")
    #Make sure we show the legend.
    plt.legend()
    #Show the plot
    plt.show()


def main():
    # TODO: Look at the code below for an example of how to do
    # API calls. I would recommend first uncommenting and
    # understanding the code, and then commenting the code back
    # out. The code is, largely, step 4.
    # base API string for weather.gov

    if len(argv) != 2:
        print("Invalid number of arguments")
        return
    

    #Set Desired Host
    hostName = argv[1]
    print("Website: " + hostName)
    hostIP = gethostbyname(hostName)
    print("IP: " + hostIP)

    #Calls whois command to get address
    command = "whois " + hostIP

    try:
        status, output = getstatusoutput(command)
    except Exception as e:
        print("An error occurred: {e}")

    chunks = output.split("# start")

    #Parses whois command to extract address
    def extract_field(text, field):
        for line in text.splitlines():
            if line.lower().startswith(field.lower()):
                return line.split(":", 1)[1].strip()
        return None
    
    x = 0
    y = 0

    for chunk in chunks:
        street = extract_field(chunk, "Address")
        city = extract_field(chunk, "City")
        state = extract_field(chunk, "State")
        zip_code = extract_field(chunk, "PostalCode")
        if(street == None):
           continue
        print("Address: " + street, city, state, zip_code)
        
        #Formats address for the geocoding URL
        address = "address=" + street + " " + city + " " + state + " " + zip_code
        address = address.replace(" ", "+")

        location_URL = "https://geocoding.geo.census.gov/geocoder/locations/onelineaddress?" + address + "&benchmark=2020&format=json"
        
        #Print Location URL for bug testing to see if address works with the API
        #print(location_URL)

        response = get(location_URL)
        js = loads(response.text)
        
        #Gets Longitude and Lattitude from result
        try:
            x = js["result"]["addressMatches"][0]["coordinates"]["x"]   
            y = js["result"]["addressMatches"][0]["coordinates"]["y"]
        except Exception as e:
            print("Invalid Address, trying next.")
            continue
        
        x = round(x, 4)
        y = round(y, 4)

        print(x,y)
        print()
        break

    #Formats coordinates for the weather URL
    weather_URL = "https://api.weather.gov/points/" + str(y) + "," + str(x)
    response = get(weather_URL)
    js = loads(response.text)

    #Finds the hourly forcast for the next 7 hours
    try:
        forecast_URL = js['properties']['forecastHourly']
    except:
        print("Cannot find Geolocation")
        return
    response = get(forecast_URL)
    js = loads(response.text)

    temp_list = []
    for i in js['properties']['periods']:
        temp_list.append(i['temperature'])

    plot_temps(temp_list)

if __name__ == "__main__":
    main()
