# -*- coding: utf-8 -*-
"""
Created on Fri May 27 17:01:35 2022

@author: Swift User
"""
#%%
import pandas as pd
import numpy as np
import re
import Monkey_Type_Detection as mtd
#consolidate all data to one - use multiprocessing to load data from various sources - to do
# open_street_address_db=pd.read_pickle('formatted_open_street_address_db.pkl')
#%%
woocom_data=pd.read_pickle('woocom.pkl')
shopify_data=pd.read_pickle('shopify_data.pkl')
formatted_open_street_address_db=pd.read_pickle('formatted_open_street_address_db.pkl')
dataset_promise_merge=pd.read_csv('dataset_promise_merge.csv')  #shipments data with mapped ndr causes - refer to autolabelling - module for this
address_shipments_data=pd.read_pickle('address_shipments_data.pkl')
#preliminary processing/parsed -  osm_data from from osm pbf data - should use osm4scala - for later extraction, processing - using pyspark
osm_parsed_data=pd.read_parquet('osm_data_preprocessed.pq')
external_gov_data_pkl=pd.read_pickle('external_gov_data_raw.pkl')
# osm_parsed_data.head()
#%%

#preprocessing methods - 
def shopify_data_preprocess(df):
    #two address lines - 
    df.loc[df['shipping_address_address1'].isnull()==False,'shipping_address_address1']=df['shipping_address_address1'].str.lower()
    df.loc[df['shipping_address_address2'].isnull()==False,'shipping_address_address2']=df['shipping_address_address2'].str.lower()
    df.loc[df['shipping_address_address1'].isnull()==True,'shipping_address_address1']='' #set empty address
    df.loc[df['shipping_address_address2'].isnull()==True,'shipping_address_address2']=''
    #get overall address
    df.loc[df['shipping_address_address1'].isnull()==False,'whole_shipping_address']=df['shipping_address_address1']+','+df['shipping_address_address2']

    #check for invalid address - frequency
    df.loc[df['shipping_address_city'].isnull()==False,'shipping_address_city']=df['shipping_address_city'].str.lower()
    df.rename(columns={'whole_shipping_address':'address','shipping_address_city':'city','shipping_address_zip':'pincode','shipping_address_latitude':'latitude','shipping_address_longitude':'longitude'},inplace=True)
    df['state']=np.nan #can be added later 
    df['status']=np.nan
    df['ndr_cat']=np.nan
    #shopify_data[['shipping_address_city','shipping_address_latitude','shipping_address_longitude']]
    address_short=df[['address','pincode','city','state','latitude','longitude','ndr_cat','status']]
    return address_short

def woocom_data_preprocess(df):
    woocom_data=df.copy()
    woocom_data.loc[woocom_data['drop_location_address'].isnull()==False,'address_string']=woocom_data['drop_location_address'].str.lower()
    woocom_data.loc[woocom_data['drop_location_address'].isnull()==True,'address_string']='' #if null set empty string
    woocom_data.rename(columns={'drop_location_pin':'drop_location_pincode'},inplace=True)
    woocom_data['latitude']=np.nan
    woocom_data['longitude']=np.nan
    woocom_data['state']=np.nan
    woocom_data['status']=np.nan
    woocom_data['ndr_cat']=np.nan
    woocom_data.rename(columns={'address_string':'address','drop_location_city':'city','drop_location_pincode':'pincode'},inplace=True)
    address_short=woocom_data[['address','pincode','city','state','latitude','longitude','ndr_cat','status']]
    return address_short
#%%
def shipments_data_preprocess(df):
    #two address lines - 
    df.loc[df['drop_location_address_1'].isnull()==False,'drop_location_address_1']=df['drop_location_address_1'].str.lower()
    df.loc[df['drop_location_address_2'].isnull()==False,'drop_location_address_1']=df['drop_location_address_1'].str.lower()
    df.loc[df['drop_location_address_1'].isnull()==True,'drop_location_address_1']='' #set empty address
    df.loc[df['drop_location_address_1'].isnull()==True,'drop_location_address_1']=''
    #get overall address
    df.loc[df['drop_location_address_1'].isnull()==False,'whole_shipping_address']=df['drop_location_address_1']+','+df['drop_location_address_2']
    # df.loc[df['drop_location_city'].isnull()==False,'drop_location_city']=df['drop_location_city'].str.lower()
    df.loc[df['drop_location_city'].isnull()==False,'drop_location_city']=df['drop_location_city'].str.lower()
    df['state']=np.nan #can be added later 
    df['status']=np.nan
    df['ndr_cat']=np.nan
    df['latitude']=np.nan
    df['longitude']=np.nan
    #map shipment status - to a broad set of categories
    
    df.loc[df['current_status'].str.contains('Delivered'),'status']='Delivered'
    df.loc[df['current_status'].str.contains('RTO'),'status']='RTO'
        
    df.loc[df['current_status'].str.contains('Lost'),'status']='Lost'
    df.loc[df['current_status'].str.contains('Damaged'),'status']='Damaged'
    df.loc[df['current_status'].str.contains('Cancelled'),'status']='Cancelled'
    #check for invalid address - frequency
    df.rename(columns={'whole_shipping_address':'address','drop_location_city':'city','drop_location_pincode':'pincode'},inplace=True)
    
    address_short=df[['address','pincode','city','state','latitude','longitude','ndr_desc_cat','status']]
    return address_short,df
#%%


def check_for_pincode_in_text(text):
    #check if a 6 digit sequence detected in the address string, if yes check for its validity
    number_sequence=''
    flag=0
    number_list=[]
    for character in text:
        if character.isdigit():
            number_sequence=number_sequence+character
            flag=1
        elif flag==1:
            number_list.append(number_sequence) # add the no sequency to a list
            number_sequence='' #reset number sequence - empty
            flag=0
    #check if a 6 digit number sequence is present - 
    for elem in number_list:
        if len(elem)==6:
            #sequence probably corresponds to the pincode info - 
            #check for pincode validity - based on regex pattern check and whether 
            #pincode is available in the database
            pincode_valid=pincode_validation(elem)
            if pincode_valid==True:
                return 1,elem
            else:
                return -1,''  #when -1 returned - detected 
                #pincode sequence is address - invalid
    return 0,''     #when no pincode sequence is detected
            
            

#%%
def remove_consecutive_commas(text):
    processed_text=''
    comma_flag=0
    first_letter=1
    i=0
    l=len(text)
    # print("l: ",l)
    for character in text:
        i=i+1
        # print("i: ",i)
        if character==',' and comma_flag==1:
            # print("yes...")
            continue
        elif character==',':
            comma_flag=1  
        else:
            comma_flag=0
        if first_letter==1 and character==',':
            # print("yes...")
            continue
        
        if i==l-1 and character==',':
            #if its the last character - skip comma insertion
            # print("yes...",character," - ",text[i-1],'prev - ',text[i-2])
            break
        # print("insert...",character,"for l - ",i)
        processed_text=processed_text+character
        first_letter=0 #reset first letter flag
        # i=i+1
    return processed_text
#%%
#%%
def osm_data_preprocess(df):
    # key_freq_df=pd.read_csv('key_freq_df.csv')
    #get the frequent tags - 
    #generate cols for all the addresses
    # import osm_data_extraction
    #read generated file - for OSM format data
    # osm_data=pd.read_parquet('open_street_map_data/overall_osm_df.pq')
    #convert to lower case - for all columns
    #here name - address, 
    #location entity/tag - hierarchy of info/location attribute, highway, junction, building, amenity, nature of location , shop type
    #lat long
    osm_parsed_data=df.copy()
    osm_df_short=osm_parsed_data[['name','place','postal_code','locality','taluk','pin_code','latitude','longitude',
    'addr_postcode',
    'addr_state',
    'addr_full',
    'addr_district',
    'addr_street',
    'addr_city',
    'addr_subdistrict',
    'addr_housenumber',
    'addr_block',
    'addr_place',
    'addr_housename',
    'addr_country']]  #list of relevant attributed for first level of validation
    
    short_osm_col_list=(osm_df_short.columns)
    
    df=osm_df_short.copy()

    for col in short_osm_col_list:
        df.loc[df[col].isnull()==True,col]='' #if nan - replace with empty string
        df[col]=df[col].astype(str) #in case the type is not already string - set to string type
        df.loc[df[col].isnull()==False,col]=df[col].str.lower() #convert text to lower case
    #combine different attributes to generate the address
    df.loc[df['name'].isnull()==False,'address_string']=df['addr_housenumber']+','+df['addr_housename']+','+df['addr_block']+','+df['addr_place']+df['addr_street']+','+df['taluk']+','+df['locality']+','+df['name']+','+df['addr_subdistrict']+','+df['addr_district']+df['addr_city']+df['addr_state']
    
    df['address']=df['address_string'].apply(lambda x: remove_consecutive_commas(x))
    # df['address'].head()
    df.loc[df['postal_code'].isnull()==False,'pincode']=df['postal_code']
    df.loc[df['pin_code'].isnull()==False,'pincode']=df['pin_code']
    df.loc[df['pincode'].isnull()==True,'pincode']=df.loc[df['pincode'].isnull()==True,'address'].apply(lambda x: check_for_pincode_in_text(x))
    df['pincode']=df['pincode'].astype(str)
    #get city, district, postalcode, location - place - tag
    df_short=df[['address','pincode']]

    #df.rename(columns={'location':''})
    return df

#%%
import re
def remove_bo_footer(x):
    pattern='...O$'
    replc=''
    string=x
    new_string=re.sub(pattern, replc, string)
    return new_string

#%%
#def dataset_
def get_all_location_tokens(text):
    promise_state_name=pd.read_parquet('promise_state_name.pq')
    promise_state_name['city']=promise_state_name['city'].str.lower()
    city_list_promise=list(promise_state_name['city'].drop_duplicates().to_numpy())
    promise_state_name['stateName']=promise_state_name['stateName'].str.lower()
    state_list_promise=list(promise_state_name['stateName'].drop_duplicates().to_numpy())

    #get all data sources - 
    postal_code_data=pd.read_csv('postal_pincode_data.csv')
    office_col_list=list()
    for col in list(postal_code_data):
        if col.find('office')!=-1:
            print(col)
            office_col_list.append(col)
    
    for col in office_col_list: #replace all the col values with .O - replace empty
        postal_code_data[col]=postal_code_data[col].apply(lambda x: get_all_location_tokens(x))
    #convert to lower case
    for col in list(postal_code_data):
        postal_code_data[col]=postal_code_data[col].astype(str) #convert to string
        postal_code_data[col]=postal_code_data[col].str.lower() #convert to lower case
    district_list=list(postal_code_data.loc[((postal_code_data['Districtname'].isnull()==False)&(postal_code_data['Districtname']!='')),'Districtname'].drop_duplicates().to_numpy())
    #replace nulls, or exclude nulls
    taluk_list=list(postal_code_data.loc[((postal_code_data['Taluk'].isnull()==False)&(postal_code_data['Taluk']!='')),'Taluk'].drop_duplicates().to_numpy())
    #'divisionname','regionname', 'circlename', 'officename'
    division_list=list(postal_code_data.loc[((postal_code_data['divisionname'].isnull()==False)&(postal_code_data['divisionname']!='')),'divisionname'].drop_duplicates().to_numpy())
    regionname_list=list(postal_code_data.loc[((postal_code_data['regionname'].isnull()==False)&(postal_code_data['regionname']!='')),'regionname'].drop_duplicates().to_numpy())
    circlename_list=list(postal_code_data.loc[((postal_code_data['circlename'].isnull()==False)&(postal_code_data['circlename']!='')),'circlename'].drop_duplicates().to_numpy())
    officename_list=list(postal_code_data.loc[((postal_code_data['officename'].isnull()==False)&(postal_code_data['officename']!='')),'officename'].drop_duplicates().to_numpy())
    #remove .o endings from office names - 
#    name_col_list=[]
#%%
osm_parsed_data_updated=pd.read_pickle('osm_parsed_data_v1.pkl')

#%%
osm_parsed_data_preprocessed=osm_data_preprocess(osm_parsed_data_updated)

#%%
osm_parsed_data=pd.read_parquet('osm_data_preprocessed.pq')
osm_parsed_data.rename(columns={'latitude':'latitude_1','longitude':'latitude'},inplace=True)
osm_parsed_data.rename(columns={'latitude_1':'longitude'},inplace=True)
#osm_data_preprocessed
osm_parsed_data.to_pickle('osm_parsed_data_v1.pkl')
osm_parsed_data_updated=pd.read_pickle('osm_parsed_data_v1.pkl')
#%%
osm_parsed_data_preprocessed=osm_data_preprocess(osm_parsed_data_updated)
#%%
#%%
def external_gov_data_pkl(df):
    pass

    
#%%    
#def osm_parsed_data_preprocess(df):
    

shopify_data_copy=shopify_data.copy()
woocom_data_copy=woocom_data.copy()

address_shipments_data_copy=address_shipments_data.copy()

shopify_data_preprocessed=shopify_data_preprocess(shopify_data)
woocom_data_preprocessed=woocom_data_preprocess(woocom_data)

#%%
shopify_data_preprocessed.to_pickle('shopify_data_preprocessed.pkl')
woocom_data_preprocessed.to_pickle('woocom_data_preprocessed.pkl')
shipments_data_preprocessed.to_pickle('shipments_data_preprocessed.pkl')

#%%
address_shipments_data=address_shipments_data_copy.copy()
shipments_data_preprocessed,shipments_data_all_preprocessed=shipments_data_preprocess(address_shipments_data)
#%%
dataset_promise_merge_updated=pd.read_pickle('dataset_promise_merge_updated.pkl')
shipments_data_with_ndr_preprocessed=shipments_data_preprocess(dataset_promise_merge)
#%%

shopify_data=shopify_data_copy.copy()
woocom_data=woocom_data.copy()
address_shipments_data=address_shipments_data.copy()
#osm, data_gov data, external shipments data - prelim preprocessing - to structuring of training data

#add - dataset_promise_merge,external_gov_data_pkl, osm_parsed_data, formatted_open_street_address_db



