# author: Jake Mowatt

from flask import Flask
from json import loads
from requests import get
from socket import gethostbyname
from subprocess import getstatusoutput

def getAddress(dn):
    #Get IP from domain_name
    hostIP = gethostbyname(dn)

    #Calls whois command to get address
    command = "whois " + hostIP

    try:
        status, output = getstatusoutput(command)
    except Exception as e:
        return("Invalid Domain Name")
    
    chunks = output.split("# start")

    #Parses whois command to extract address
    def extract_fields(text, field):
        results = []
        field_lower = field.lower()

        for line in text.splitlines():
            line_stripped = line.strip()
            if line_stripped.lower().startswith(field_lower):
                # Remove the field name and optional colon
                value = line_stripped[len(field):].lstrip(": ").strip()
                results.append(value)

        return results

    for chunk in chunks:
        street = extract_fields(chunk, "Address")
        city = extract_fields(chunk, "City")
        state = extract_fields(chunk, "StateProv")
        zip_code = extract_fields(chunk, "PostalCode")
        
        if (len(street) > 1 and 'P.O.' in street[1]):
            continue

    return(street[0] + " " + city[0] + ", " + state[0] + " " + zip_code[0])

def getWeather(dn):
    #Gets address from IP
    address = getAddress(dn)

    #Formats address for the geocoding URL
    address = "address=" + address
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
        print("No geocoding match found for this address.")
        return
    
    x = round(x, 4)
    y = round(y, 4)

    #Formats coordinates for the weather URL
    weather_URL = "https://api.weather.gov/points/" + str(y) + "," + str(x)
    response = get(weather_URL)
    js = loads(response.text)

    #Finds the hourly forcast for the next 7 hours
    forecast_URL = js['properties']['forecast']
    response = get(forecast_URL)
    js = loads(response.text)
    
    return js['properties']['periods'][0]['detailedForecast']

def getRange(dn):
    #Get IP from domain_name
    hostIP = gethostbyname(dn)

    #Calls whois command to get address
    command = "whois " + hostIP

    try:
        status, output = getstatusoutput(command)
    except Exception as e:
        return("Invalid Domain Name")
    
    #Parses whois command to extract address
    def extract_field(text, field):
        for line in text.splitlines():
            if line.lower().startswith(field.lower()):
                return line.split(":", 1)[1].strip()
        return None
    
    return extract_field(output, "NetRange")

addressCache = {}
weatherCache = {}
rangeCache = {}

app = Flask(__name__)

@app.route('/')
def home():
    return "Available API Calls: 1. /address/domain_name 2. /weather/domain_name 3. /range/domain_name"

@app.route("/address/<domain_name>")
def address(domain_name):
    if domain_name in addressCache:
        return "Cached: " + addressCache[domain_name]
    else:
        addressCache[domain_name] = getAddress(domain_name)
        return addressCache[domain_name]

@app.route("/weather/<domain_name>")
def weather(domain_name):
    if domain_name in weatherCache:
        return "Cached: " + weatherCache[domain_name]
    else:
        weatherCache[domain_name] = getWeather(domain_name)
        return weatherCache[domain_name]

@app.route("/range/<domain_name>")
def range(domain_name):
    if domain_name in rangeCache:
        return "Cached: " + rangeCache[domain_name]
    else:
        rangeCache[domain_name] = getRange(domain_name)
        return rangeCache[domain_name]


if __name__ == "__main__":
    app.run()
