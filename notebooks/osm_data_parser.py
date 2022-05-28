# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

#import required libraries
import math
import numpy as np
import pandas as pd
import re
import pyphonetics
import phonetics
import pydata_google_auth
import Monkey_Type_Detection as mtd
from arcgis.gis import GIS
from getpass import getpass
import skimpy
import wikipedia as wiki
import requests
from arcgis.geocoding import batch_geocode, Geocoder, get_geocoders, batch_geocode, geocode
from google_trans_new import google_translator

key_freq_df=pd.read_csv('key_freq_df.csv')
key_freq_df.sort_values(by='frequency',ascending=False,inplace=True) #sort OSM data key and corresponding
#frequency in decreasing order
key_freq_df.head()
key_freq_list=list(key_freq_df.loc[key_freq_df['frequency']>1000,'key'].to_numpy()) #list of frequent keys
key_freq_list
#display all address related tags - 
address_tags=[]  #extracting all the address related tags - attributes specific to an address
for key in key_freq_list:
    if key.find('addr:')!=-1:
        print("tag: ",key)
        address_key=key.split('addr:')[1]
        address_tags.append(address_key)

print("no of frequently occuring tags - ",len(key_freq_list)) 
print("no of addresses - from OSM data: ",key_freq_df['frequency'].sum())
#161 - keys that occur for more than 1K addresses

#OSM data feature extraction - add all these high frequency keys as columns in OSM df
osm_cols=['location','tags','name','latitude','longitude'] #first set of attributes extracted from OSM data
osm_col_list=osm_cols

for key in key_freq_list:
    if key not in osm_cols:
        key=key.replace(':','_')  #replace ':' with '_' for column names
        osm_col_list.append(key)  #add other frequent tags to OSM Data column list
osm_col_list
#create OSM dataframe - with the above column list - 
osm_data=pd.DataFrame(columns=osm_col_list)
# osm_data[osm_col_list]=np.nan

pd.set_option('display.max_columns',None)
osm_data
#add data from osm tag list in the above dataframe


import osmium
# osm_df=pd.DataFrame(columns={'lat_long','name','tags'})
osm_data_count=0
osm_file_count=0
overall_osm_df=pd.DataFrame(columns=osm_col_list) #to store all data combined
osm_df=pd.DataFrame(columns=osm_col_list)
class NamesHandler(osmium.SimpleHandler):
    def node(self, n):
        if 'name' in n.tags:
            #print("osm row ",osm_row)
#             osm_row=pd.DataFrame(columns=osm_col_list)
            osm_dict = dict.fromkeys(osm_col_list, None) #initialize dictionary with OSM data
            osm_dict['latitude']=str(n.location).rpartition('/')[0]
            osm_dict['longitude']=str(n.location).rpartition('/')[2]
            osm_dict['name']=str(n.tags['name'])
            osm_dict['tags']=str(dict(n.tags))
            osm_dict['location']=str(n.location)
            print("osm_dict - ",osm_dict)
            #set values for other location attributes - 
            tag_dict=dict(n.tags)
            tag_keys=list(tag_dict.keys())
            for key in tag_keys:
                if key in osm_col_list: #only add frequent tags to osm data
                    osm_dict[key]=tag_dict[key]
            osm_row=pd.DataFrame(osm_dict,index=[0]) #set osm data row from osm dictionary
            global osm_df
            global osm_data_count
            osm_df=pd.concat([osm_df,osm_row])
            osm_data_count=osm_data_count+1 # increment for every new OSM data row
            if osm_data_count%2000==0 :
#                 osm_data_factor=osm_data_count
                global osm_file_count
                
                osm_file_count=osm_file_count+1
                print("file count - ",osm_data_count)
                print("osm_row: ",osm_row)
                osm_df.to_parquet('osm_parsed_data/osm_df_'+str(osm_file_count)+'.pq')
        
import swifter
def main(osmfile):
    NamesHandler().apply_file(osmfile)
    return 0

main('india-latest.osm.pbf')
