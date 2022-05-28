# -*- coding: utf-8 -*-
"""
Created on Sat May 28 11:03:24 2022

@author: Swift User
"""

import pandas as pd
import numpy as np
import re
import Monkey_Type_Detection as mtd
#consolidate all data to one - use multiprocessing to load data from various sources - to do
# open_street_address_db=pd.read_pickle('formatted_open_street_address_db.pkl')
#%%
"""
woocom_data=pd.read_pickle('woocom.pkl')
shopify_data=pd.read_pickle('shopify_data.pkl')
formatted_open_street_address_db=pd.read_pickle('formatted_open_street_address_db.pkl')
dataset_promise_merge=pd.read_csv('dataset_promise_merge.csv')  #shipments data with mapped ndr causes - refer to autolabelling - module for this
address_shipments_data=pd.read_pickle('address_shipments_data.pkl')
#preliminary processing/parsed -  osm_data from from osm pbf data - should use osm4scala - for later extraction, processing - using pyspark
osm_parsed_data=pd.read_parquet('osm_data_preprocessed.pq')
external_gov_data_pkl=pd.read_pickle('external_gov_data_raw.pkl')
# osm_parsed_data.head()
"""
shopify_data_preprocessed=pd.read_pickle('shopify_data_preprocessed.pkl')
shopify_data_preprocessed.head()
#%%
import Monkey_Type_Detection as mtd
def suspect_monkey_typing(x):
    is_monkey_type=mtd.detect_one_hand_monkey_typing(x)
    is_gibberish=mtd.gibberish_text_detection(x)
    print("is text identified as gibberish...", is_gibberish)
    print("is text identified to be monkey typed... ",is_monkey_type)
    #third most imp validation - check if text has high similarity or exact match in location dictionary - even if pred
    #as gibberish or monkey typed
    #valid_token=is_text_present_in_location_db(x) - to be added
    return is_monkey_type or is_gibberish  # or valid_token
#%%
import swifter
shopify_data_preprocessed['monkey_typing_suspected']=shopify_data_preprocessed['address'].swifter.apply(lambda x: suspect_monkey_typing(x))
##%%
#%%
shopify_data_preprocessed.groupby('monkey_typing_suspected',dropna=False).size()
#%%
import swifter

test_sample=shopify_data_preprocessed.head(100)
test_sample['monkey_typing_suspected']=test_sample['address'].swifter.apply(lambda x: suspect_monkey_typing(x))
#%%
test_sample.groupby('monkey_typing_suspected',dropna=False).size()
#%%
test_sample.loc[test_sample['monkey_typing_suspected']==True,'address']
#%%