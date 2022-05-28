# -*- coding: utf-8 -*-
"""
Created on Thu May 26 20:43:26 2022

@author: Swift User
"""

#generate an exhaustive location dictionary - including as many location tokens as possible
#get all location info - from all sources combined

#consolidate all data to one - use multiprocessing to load data from various sources - to do
# open_street_address_db=pd.read_pickle('formatted_open_street_address_db.pkl')
def read_from_all_data_sources():
        woocom_data=pd.read_pickle('woocom.pkl')
        shopify_data=pd.read_pickle('shopify_data.pkl')
        formatted_open_street_address_db=pd.read_pickle('formatted_open_street_address_db.pkl')
        dataset_promise_merge=pd.read_csv('dataset_promise_merge.csv')  #shipments data with mapped ndr causes - refer to autolabelling - module for this
        address_shipments_data=pd.read_pickle('address_shipments_data.pkl')
        #preliminary processing/parsed -  osm_data from from osm pbf data - should use osm4scala - for later extraction, processing - using pyspark
        osm_parsed_data=pd.read_parquet('osm_data_preprocessed.pq')
        external_gov_data_pkl=pd.read_pickle('external_gov_data_raw.pkl')
        # osm_parsed_data.head()
        promise_data=pd.read_parquet('promise_state_name.pq')
        dataset_promise_merge=pd.read_csv('dataset_promise_merge.csv')
        postal_pincode_data=pd.read_csv('postal_pincode_data.csv')

#def preprocessed_data_sources():
 
import swifter
import pandas as pd
from geopy.geocoders import Nominatim
import numpy as np
def string_encode(x):
    return x.encode("utf-8")
def fwd_geocode_address_geopy_osm(address):
    location=''
    geolocator = Nominatim(user_agent="fwd_geocoding")
    print(address)
    location = geolocator.geocode(address)
    return location
df=pd.read_parquet('current_osm_address.pq')
df['geopy_location']=np.nan
df.loc[df['address'].isnull()==False,'address']=df['address'].apply(lambda x: string_encode(x)) #encode the address strings
df['geopy_location']=df['address'].swifter.apply(lambda x: fwd_geocode_address_geopy_osm(x))
df[['address','latitude','longitude','geopy_location']].head()