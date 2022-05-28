# -*- coding: utf-8 -*-
"""
Created on Sat May 28 09:47:18 2022

@author: Swift User
"""
#%%
import csv
import pandas as pd
import googlemaps
#%%

#get address column from data - 
gmaps_key = googlemaps.Client(key="AIzaSyBn8fz5Ex7CMnC833482t5tLcwf87NLNsk")
#try geocoding for an address
add_1 = "UrbanVault 761, HSR Layout, Sector 3,"

def google_fwd_geocoding(x): #pass address string as parameter
        g = gmaps_key.geocode(x)
        lat = g[0]["geometry"]["location"]["lat"]
        long = g[0]["geometry"]["location"]["lng"]
        print('Latitude: '+str(lat)+', Longitude: '+str(long))
        latlong=()
        latlong=[lat,long]
        latlong=tuple(latlong)
        #latlong.append(lat)
        #latlong.append(long)
        return latlong
import reverse_geocoder as rg
#latlong=google_fwd_geocoding(add_1)
result = rg.search(latlong)
pprint.pprint(result)

print("reverse...",result)
#latlng=12.9103599,77.6447568
#g = gmaps_key.geocode(latlng)
#print("reverse geocode output - ",g)
#%%


#%%
import reverse_geocoder as rg
import pprint
 
def reverseGeocode(coordinates):
    result = rg.search(coordinates)
     
    # result is a list containing ordered dictionary.
    pprint.pprint(result)
 
# Driver function
if __name__=="__main__":
     
    # Coordinates tuple.Can contain more than one pair.
    coordinates =latlng
     
    reverseGeocode(coordinates)
#%%
#import url
import requests
import urllib
#data = data[['Locality']]
add_1 = "UrbanVault 761, HSR Layout, Sector 3, 560102"
add_1='Century City Mall, Poblacian, Makati City'
URL = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(add_1) +'?format=json'
response = requests.get(URL).json()
print(URL)
print("response object... - ",response)
#print('Latitude: '+response[0]['lat']+', Longitude: '+response[0]['lon'])
#%%