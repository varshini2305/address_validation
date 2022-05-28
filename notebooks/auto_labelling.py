# -*- coding: utf-8 -*-
"""
Created on Thu May 26 19:29:18 2022

@author: Swift User
"""
import pandas as pd
import numpy as np
import re
import Monkey_Type_Detection as mtd
#labelling - data - with/without address issue - 
"""
1. based on shipment status
2. based on address issue identified
3. based on address location (based on tier) - and amount of address info


if we don't have any info - on address issue - we only label based on - status,
and basic address format checks

steps - structure the input address data for labelling - to std format

1. i.e. address string, pincode, city, tier, state, latitude, longitude, ndr_cat, attempts, shipment_status - 
last two if available - else set to nan

"""
def any_non_empty_elem(text_list):
    for text in text_list:
        if text!='' or text!=np.nan:
            return True  #even if there is one non-empty element in the list - return true
    return False
def detect_delim(text):
    print("text test: ",text)
    print("text type - -",type(text))
    text=str(text)
    split_string = re.split(r',|!|;|-|:|_| |\t|\n', text)
    print(text)
    print(split_string)
    if len(split_string)==1:
        return -1  #no delimiters present in the text
    elif any_non_empty_elem(split_string)==False:
        return 0 #no non-delimiters present in the text
    return 1  #if there are one or more delimiters, 
#and there is at least one non-empty element - excluding the delimiters

def regex_match(pincode,pattern):
    if re.match(pincode, pattern):
        return True
    else:
        return False


def check_pincode_correct(pincode, address=''):
    pincode=str(pincode) #convert the input pincode - into string format, if not already - the first digit in pincode is zero - it will be removed, and pincode - will be read as 5 digits
    #check if it has 6 digits
    try:
            if len(pincode)<6:
                raise Exception("Invalid pincode - pincode contains less than 6 digits")
            elif len(pincode)>6:
                raise Exception("Pincode cannot have more than 6 digits...")
            elif pincode[0]=='0':
                raise Exception("First digit of pincode cannot be zero...")
            pincode_pattern=r"^[1-9]{1}[0-9]{2}\s{0,1}[0-9]{3}$"
            pincode_pattern_valid=regex_match(pincode_pattern,pincode)
            if (pincode_pattern_valid==False):
                raise Exception("Pincode Format not valid...")
            else: #entered pincode format is valid
                #now check if the entered pincode present in promise or postal database -
                postal_pincode_df=pd.read_csv('postal_pincode_data.csv')
                #convert both postal pincode and promise pincode list - to str types - to append both lists
                postal_pincode_df['pincode']=postal_pincode_df['pincode'].astype(str)
                postal_pincode_list=list(postal_pincode_df['pincode'].drop_duplicates().to_numpy())
                print("len of postal_pincode_list: ",len(postal_pincode_list))
        
                promise_pincode_df=pd.read_parquet('promise_state_name.pq')
                promise_pincode_df['pincode']=promise_pincode_df['pincode'].astype(str)
                promise_pincode_list=list(promise_pincode_df['pincode'].drop_duplicates().to_numpy())
                print("len of promise_pincode_list: ",len(promise_pincode_list))
                #get combined list of two pincodes -
                pincode_list=list(set(postal_pincode_list)|set(promise_pincode_list))
                print("len of pincode list: ",len(pincode_list))
        
                print("checking if pincode present in exhaustive list pincodes - db....")
                #check if pincode present in the overall pincode list -
                if pincode not in pincode_list:
                    raise Exception("Pincode not found in database...")
                else:
                    #now if the format of the entered pincode is valid and if it is also found in the overall pincode database...
                    #Next step is to see if the pincode matches - the entered address
                    #Two ways to check -
                    # if the city matches pincode
                    # if the locality or other smaller - division - mapped to a pincode - based on postal pincode data
                    print("pincode entered is valid...")
                    print("Pincode Address Match Check - yet to check if locality/address string matches with the entered pincode....")
                    """
                                Postal data - attributes -
                                officename	pincode	officeType	Deliverystatus	divisionname regionname	circlename	Taluk	Districtname	statename	Telephone	Related Suboffice	Related Headoffice	longitude	latitude
        
                    """
                    return True #if no exceptions are raised then the input pincode is valid
    except Exception:
        return False       #if any of the above exceptions are raised - pincode - is invalid     


def pincode_validation(pincode,address=''):
    # pincode_format_valid=check_pincode_format(pincode)
    pincode_address_valid=check_pincode_correct(pincode)
    return pincode_address_valid


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
            
            
    
            
            
def split_by_delimiters(address_string):
    print("address_string: ",address_string)
    print("address_string type: ",type(address_string))
    split_string = re.split(r',|!|;|-|:|_| |\t|\n', address_string)
    
    print(address_string)
    print(split_string)
    return split_string #return lexical units - split by various delimiters


    
def isEnglish(s):
    return s.isascii()
    
def check_if_there_is_address_issue(address_string):
    if len(address_string)<10:
        return 'yes'   #'valid_address_format_check_level_one' #length of address two short
    elif detect_delim(address_string)!=1:
        return 'yes'
    elif check_for_pincode_in_text(address_string)==-1:
        return 'yes'
    elif isEnglish(address_string)==False:
        return 'yes'
    elif mtd.detect_one_hand_monkey_typing(address_string)==True:  #in one hand msd - include - location dict along with enchant/oxford dict check
        return 'yes'
    else :
        return ''
#%%
def set_tier():
        tier_1=[
        'bangalore',
        'bengaluru',
        'chennai',
        'delhi',
        'hyderabad',
        'kolkata',
        'mumbai',
        'ahmedabad',
        'pune'
        ]
        tier_2=['Agra',
        'Ajmer',
        'Aligarh',
        'Amravati',
        'Amritsar',
        'Asansol',
        'Aurangabad',
        'Bareilly',
        'Belgaum',
        'Bhavnagar',
        'Bhiwandi',
        'Bhopal',
        'Bhubaneswar',
        'Bikaner',
        'Bilaspur',
        'Bokaro Steel City',
        'Chandigarh',
        'Coimbatore',
        'Cuttack',
        'Dehradun',
        'Dhanbad',
        'Bhilai',
        'Durgapur',
        'Erode',
        'Faridabad',
        'Firozabad',
        'Ghaziabad',
        'Gorakhpur',
        'Gulbarga',
        'Guntur',
        'Gwalior',
        'Gurgaon',
        'Guwahati',
        'Hamirpur',
        'Hubli–Dharwad',
        'Indore',
        'Jabalpur',
        'Jaipur',
        'Jalandhar',
        'Jammu',
        'Jamnagar',
        'Jamshedpur',
        'Jhansi',
        'Jodhpur',
        'Kakinada',
        'Kannur',
        'Kanpur',
        'Kochi',
        'Kolhapur',
        'Kollam',
        'Kozhikode',
        'Kurnool',
        'Ludhiana',
        'Lucknow',
        'Madurai',
        'Malappuram',
        'Mathura',
        'Goa',
        'Mangalore',
        'Meerut',
        'Moradabad',
        'Mysore',
        'Nagpur',
        'Nanded',
        'Nashik',
        'Nellore',
        'Noida',
        'Patna',
        'Pondicherry',
        'Purulia Prayagraj',
        'Raipur',
        'Rajkot',
        'Rajahmundry',
        'Ranchi',
        'Rourkela',
        'Salem',
        'Sangli',
        'Shimla',
        'Siliguri',
        'Solapur',
        'Srinagar',
        'Surat',
        'Thiruvananthapuram',
        'Thrissur',
        'Tiruchirappalli',
        'Tiruppur',
        'Ujjain',
        'Bijapur',
        'Vadodara',
        'Varanasi',
        'Vasai-Virar City',
        'Vijayawada',
        'Visakhapatnam',
        'Vellore',
        'Warangal']
        tier_2_lower=[]
        for x in tier_2:
            x=x.lower()
            tier_2_lower.append(x)
        # tier_2_lower
        promise_state_name=pd.read_parquet('promise_state_name.pq')

        promise_state_name['city']=promise_state_name['city'].str.lower()
        
        total_city_list=list(promise_state_name['city'].drop_duplicates().to_numpy())
        len(total_city_list)
        tier_3=list(set(total_city_list)-set(tier_1)-set(tier_2_lower))
        print("tier 1 city length: ",len(tier_1)) #tier 1 city count
        print("tier 2 city length: ",len(tier_2_lower)) #tier 2 city count
        print("tier 3 city list: ",len(tier_3)) #tier 3 city count
        # tier_3=total_city_list
        return tier_1,tier_2_lower,tier_3
#%%
def str_lower(x):
    if pd.isna(x)==False:
        return x.lower()
    else: return x

#%%          
def set_ndr_issue(dataset):
        #set ndr cat attribute using - ndr desc, desc path, ndr status - values - set if address issue/none
        
        #set vendor partner
        #data segmentation
        #dataset used from - Jan 02 '21 - May 02 '22
        #set partner
        dataset.loc[dataset['vendor_cid'].str.contains('DELHIVERY'),'partner']='DELHIVERY'
        dataset.loc[dataset['vendor_cid'].str.contains('XPRESSBEES'),'partner']='XPRESSBEES'
        dataset.loc[dataset['vendor_cid'].str.contains('AMAZON'),'partner']='AMAZON'
        dataset.loc[dataset['vendor_cid'].str.contains('BLUEDART'),'partner']='BLUEDART'
        
        dataset.loc[dataset['vendor_cid'].str.contains('EKART'),'partner']='EKART'
        dataset.loc[dataset['vendor_cid'].str.contains('SHADOW'),'partner']='SHADOW_FAX'
        
        dataset.loc[dataset['vendor_cid'].str.contains('DUNZO'),'partner']='DUNZO'
        dataset.loc[dataset['vendor_cid'].str.contains('FEDEX'),'partner']='FEDEX'
        
        #get correct pincode from list
        shipped_pincode_list=list(dataset['drop_location_pincode'].drop_duplicates().to_numpy())
        #promise_state_name mapping
        promise_state_name=pd.read_parquet('promise_state_name.pq')
        len(promise_state_name)
        promise_state_name['pincode']=promise_state_name['pincode'].astype(float).astype(int)
        promise_state_name.head()
        promise_pincode_list=list(promise_state_name['pincode'].drop_duplicates().to_numpy())
        dataset_promise_merge=dataset.merge(promise_state_name,left_on='drop_location_pincode',right_on='pincode',how='left')
        tier_1,tier_2,tier_3=set_tier()
        dataset_promise_merge.loc[dataset_promise_merge['city'].isin(tier_1),'tier']=1
        dataset_promise_merge.loc[dataset_promise_merge['city'].isin(tier_2),'tier']=2
        dataset_promise_merge.loc[dataset_promise_merge['city'].isin(tier_3),'tier']=3
        dataset_promise_merge['lastNdrDesc']=dataset_promise_merge['lastNdrDesc'].apply(lambda x: str_lower(x))
        dataset_promise_merge['ndr_desc_cat']=np.nan
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrDesc'].str.contains('address'))&((dataset_promise_merge['lastNdrDesc'].str.contains('incomplete'))|(dataset_promise_merge['lastNdrDesc'].str.contains('issue'))|(dataset_promise_merge['lastNdrDesc'].str.contains('incorrect')))),'ndr_desc_cat']='address issue'
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrDesc'].str.contains('address'))&((dataset_promise_merge['lastNdrDesc'].str.contains('unlocatable'))|(dataset_promise_merge['lastNdrDesc'].str.contains('mismatch'))|(dataset_promise_merge['lastNdrDesc'].str.contains('bde hal'))|(dataset_promise_merge['lastNdrDesc'].str.contains('invalid')))),'ndr_desc_cat']='address issue'
        # set ndr cat based on above - identified reason - as a substring
        dataset_promise_merge.loc[dataset_promise_merge['lastNdrDesc'].str.contains('customer not available at given address and not reachable over phone')==True,'ndr_desc_cat']='customer_contact_issue'
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrDesc'].str.contains('no such consignee at the given address'))|(dataset_promise_merge['lastNdrDesc'].str.contains('no such co./cnee at given address'))),'ndr_desc_cat']='customer_not_available_in_given_address'


        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrDesc'].str.contains('customer wants delivery at different address'))|(dataset_promise_merge['lastNdrDesc'].str.contains('c\'nee shifted from the given address'))|(dataset_promise_merge['lastNdrDesc'].str.contains('cnee shifted from the given address'))|(dataset_promise_merge['lastNdrDesc'].str.contains('consignee moved. alternate address required'))),'ndr_desc_cat']='customer_address_changed'
        
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrDesc'].str.contains('fake booking/fake address'))|((dataset_promise_merge['lastNdrDesc'].str.contains('fake'))&(dataset_promise_merge['lastNdrDesc'].str.contains('address')))),'ndr_desc_cat']='fake_address'
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrDesc'].str.contains('fake booking/fake address'))|((dataset_promise_merge['lastNdrDesc'].str.contains('fake'))&(dataset_promise_merge['lastNdrDesc'].str.contains('address')))),'ndr_desc_cat']='fake_address'
        #dataset_promise_merge.loc[((dataset_promise_merge['lastNdrDesc'].str.contains('address'))&(dataset_promise_merge['ndr_desc_cat'].isnull()==True))].groupby(['lastNdrDesc','current_status'],dropna=False).size().sort_values(ascending=False)
        dataset_promise_merge.loc[(dataset_promise_merge['lastNdrDesc'].str.contains('misroute, due to address is closer to other svc. destination')==True),'ndr_desc_cat']='address_issue_corrected'
        #dataset_promise_merge.loc[(dataset_promise_merge['lastNdrDesc'].str.contains('misroute, due to address is closer to other svc. destination')==True),'ndr_desc_cat']='address_issue_corrected'
        dataset_promise_merge.loc[dataset_promise_merge['lastNdrDesc'].str.contains('add incomplete')==True,'ndr_desc_cat']='address_incomplete'

        dataset_promise_merge.loc[dataset_promise_merge['lastNdrDesc'].str.contains('wrong pincode')==True,'ndr_desc_cat']='address_issue(wrong_pincode)'
        
        dataset_promise_merge.loc[dataset_promise_merge['desc_path'].isnull()==False,'end_desc_path']=dataset_promise_merge.loc[dataset_promise_merge['desc_path'].isnull()==False,'desc_path'].apply(lambda x: x[-75:])
        
        dataset_promise_merge.loc[dataset_promise_merge['desc_path'].isnull()==False,'end_desc_path']=dataset_promise_merge.loc[dataset_promise_merge['desc_path'].isnull()==False,'end_desc_path'].apply(lambda x: x.lower())
        
        # dataset_promise_merge['end_desc_path']=dataset_promise_merge['end_desc_path'].apply(lambda x: x.lower())
        
        # dataset_promise_merge['ndr_desc_cat']=np.nan
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('address'))&((dataset_promise_merge['end_desc_path'].str.contains('incomplete'))|(dataset_promise_merge['end_desc_path'].str.contains('issue'))|(dataset_promise_merge['end_desc_path'].str.contains('incorrect')))),'ndr_desc_cat']='address issue'
        
        # dataset_promise_merge.groupby('ndr_desc_cat',dropna=False).size()
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('address'))&((dataset_promise_merge['end_desc_path'].str.contains('unlocatable'))|(dataset_promise_merge['end_desc_path'].str.contains('mismatch'))|(dataset_promise_merge['end_desc_path'].str.contains('bde hal'))|(dataset_promise_merge['end_desc_path'].str.contains('invalid')))),'ndr_desc_cat']='address issue'
        ndr_cat_for_other_address_issue=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('address'))&(dataset_promise_merge['ndr_desc_cat']!='address issue'))].groupby('end_desc_path',dropna=False).size().sort_values(ascending=False).reset_index()
        # set ndr cat based on above - identified reason - as a substring
        dataset_promise_merge.loc[dataset_promise_merge['end_desc_path'].str.contains('customer not available at given address and not reachable over phone')==True,'ndr_desc_cat']='customer_contact_issue'
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('no such consignee at the given address'))|(dataset_promise_merge['end_desc_path'].str.contains('no such co./cnee at given address'))),'ndr_desc_cat']='customer_not_available_in_given_address'
        
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('customer wants delivery at different address'))|(dataset_promise_merge['end_desc_path'].str.contains('c\'nee shifted from the given address'))|(dataset_promise_merge['end_desc_path'].str.contains('cnee shifted from the given address'))|(dataset_promise_merge['end_desc_path'].str.contains('consignee moved. alternate address required'))),'ndr_desc_cat']='customer_address_changed'
        
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('fake booking/fake address'))|((dataset_promise_merge['end_desc_path'].str.contains('fake'))&(dataset_promise_merge['end_desc_path'].str.contains('address')))),'ndr_desc_cat']='fake_address'
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('fake booking/fake address'))|((dataset_promise_merge['end_desc_path'].str.contains('fake'))&(dataset_promise_merge['end_desc_path'].str.contains('address')))),'ndr_desc_cat']='fake_address'
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&dataset_promise_merge['end_desc_path'].str.contains('misroute, due to address is closer to other svc. destination')==True),'ndr_desc_cat']='address_issue_corrected'
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&dataset_promise_merge['end_desc_path'].str.contains('misroute, due to address is closer to other svc. destination')==True),'ndr_desc_cat']='address_issue_corrected'
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&dataset_promise_merge['end_desc_path'].str.contains('address on package is different from  hq address')==True),'ndr_desc_cat']='wrong_address'
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&dataset_promise_merge['end_desc_path'].str.contains('rerouted to revised delivery address')==True),'ndr_desc_cat']='address_issue_corrected'
        
        # dataset_promise_merge=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('address')==False)|(dataset_promise_merge['ndr_desc_cat'].isnull()==False))]
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('add incomplete')==True)),'ndr_desc_cat']='address_incomplete'
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus'].str.contains('Address Issue'))&(dataset_promise_merge['end_desc_path'].str.contains('wrong pincode')==True)),'ndr_desc_cat']='address_issue(wrong_pincode)'
        
        # dataset_promise_merge.loc[dataset_promise_merge['lastNdrDesc']=='undelivered shipment held at location'].groupby(['lastNdrStatus','current_status'],dropna=False).size()
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['desc_path'].str.contains('DELIVERY ATTEMPTED-PREMISES CLOSED'))&(dataset_promise_merge['current_status'].str.contains('RTO'))&(dataset_promise_merge['ndr_desc_cat'].isnull()==True)),'ndr_desc_cat']='premise_closed_for_given_address'
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['end_desc_path'].str.contains('premises closed'))&(dataset_promise_merge['current_status'].str.contains('RTO'))&(dataset_promise_merge['ndr_desc_cat'].isnull()==True)),'ndr_desc_cat']='premise_closed_for_given_address'
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['desc_path'].str.contains('premises closed'))&(dataset_promise_merge['current_status'].str.contains('RTO'))&(dataset_promise_merge['ndr_desc_cat'].isnull()==True)),'ndr_desc_cat']='premise_closed_for_given_address'
        
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['ndr_desc_cat'].isnull()==True)&(dataset_promise_merge['desc_path'].str.contains('WRONG PIN'))),'ndr_desc_cat']='address_issue(wrong_pincode)'
        
        dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['ndr_desc_cat'].isnull()==True)&(dataset_promise_merge['desc_path'].str.contains('address_issue(wrong_pincode)')==True)),'ndr_desc_cat']='address_issue(wrong_pincode)'
        
        
        dataset_promise_merge.loc[dataset_promise_merge['current_status'].str.contains('Delivered'),'status']='Delivered'
        dataset_promise_merge.loc[dataset_promise_merge['current_status'].str.contains('RTO'),'status']='RTO'
        
        dataset_promise_merge.loc[dataset_promise_merge['current_status'].str.contains('Lost'),'status']='Lost'
        dataset_promise_merge.loc[dataset_promise_merge['current_status'].str.contains('Damaged'),'status']='Damaged'
        dataset_promise_merge.loc[dataset_promise_merge['current_status'].str.contains('Cancelled'),'status']='Cancelled'


        for city in tier_2:
            dataset_promise_merge.loc[dataset_promise_merge['city'].str.contains(city),'tier']=2

        dataset_promise_merge_segments=dataset_promise_merge.groupby(['tier','lastNdrStatus','shipping_attempts','status','ndr_desc_cat'],dropna=False).size().sort_values(ascending=False).reset_index()
        dataset_promise_merge_segments.rename(columns={0:'shipment_volume'},inplace=True)
        
        address_issue_dataset=dataset_promise_merge.loc[dataset_promise_merge['lastNdrStatus']=='Address Issue']
        
        
        address_issue_dataset_segments=address_issue_dataset.groupby(['tier','lastNdrStatus','shipping_attempts','status','ndr_desc_cat'],dropna=False).size().sort_values(ascending=False).reset_index()
        address_issue_dataset_segments.rename(columns={0:'shipment_volume'},inplace=True)
        return dataset_promise_merge
#%%
#test with sample shipments data
#address_shipments_data=pd.read_pickle('shipments_data_preprocessed.pkl')
address_shipments_data=pd.read_pickle('address_shipments_data.pkl')

#%%
address_issue_cat=set_ndr_issue(address_shipments_data)
address_issue_cat.loc[((address_issue_cat['lastNdrStatus']=='Address Issue')&(address_issue_cat['ndr_desc_cat'].isnull()==True)),'ndr_desc_cat']='address issue' # if specific address issue not identified
#still set the ndr cat - as address issue based on ndr status remark - for now
#for now consider all 

#%%   
#%%
def shipments_data_preprocess(df):
    #two address lines - 
    df.loc[df['drop_location_address_1'].isnull()==False,'drop_location_address_1']=df['drop_location_address_1'].str.lower()
    df.loc[df['drop_location_address_2'].isnull()==False,'drop_location_address_2']=df['drop_location_address_2'].str.lower()
    df.loc[df['drop_location_address_1'].isnull()==True,'drop_location_address_1']='' #set empty address
    df.loc[df['drop_location_address_2'].isnull()==True,'drop_location_address_2']=''
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
address_issue_cat_preprocessed=pd.DataFrame()
#%%
import swifter
#import data_preparation as dp
def label_by_attributes(address_data):
    #target label - address_issue
    
    address_issue_cat=set_ndr_issue(address_data)
    address_issue_cat.loc[((address_issue_cat['lastNdrStatus']=='Address Issue')&(address_issue_cat['ndr_desc_cat'].isnull()==True)),'ndr_desc_cat']='address issue' # if specific address issue not identified
    address_issue_cat['address_issue']=np.nan
    """
    if ndr_cat - available - use that info as well,
    if the address data comes from a std address data base - consider that a good quality 
    address.
    """
    #else address_issue - not identified by remark
    #address_issue_cat['address'].apply(valid_address_format_check_level_one)
    global address_issue_cat_preprocessed
    address_issue_cat_preprocessed_short,address_issue_cat_preprocessed_full=shipments_data_preprocess(address_issue_cat)
    
    address_issue_cat_preprocessed_full.loc[address_issue_cat_preprocessed_full['ndr_desc_cat'].isnull()==True,'ndr_desc_cat']='' #set empty string
    address_issue_cat_preprocessed_full.loc[address_issue_cat_preprocessed_full['ndr_desc_cat'].str.contains('address'),'address_issue']='yes'
    address_issue_cat_preprocessed_full
    address_issue_cat_preprocessed_full['address_issue']=address_issue_cat_preprocessed_full['address'].swifter.apply(lambda x: check_if_there_is_address_issue(x))
    col_list=list(address_issue_cat_preprocessed_short.columns)
    col_list.append('lastNdrStatus')
    col_list.append('ndr_desc_cat')
    col_list.append('tier')
    col_list.append('status')
    col_list.append('shipping_attempts')
    col_list.append('address_issue')


    address_issue_cat_preprocessed_final=address_issue_cat_preprocessed_full[col_list]
    dataset_promise_merge_segments=address_issue_cat.groupby(['tier','lastNdrStatus','shipping_attempts','status','ndr_desc_cat'],dropna=False).size().sort_values(ascending=False).reset_index()
    dataset_promise_merge_segments.rename(columns={0:'shipment_volume'},inplace=True)
        
    address_issue_dataset=address_issue_cat.loc[address_issue_cat['lastNdrStatus']=='Address Issue']
    address_issue_dataset_segments=address_issue_dataset.groupby(['tier','lastNdrStatus','shipping_attempts','status','ndr_desc_cat'],dropna=False).size().sort_values(ascending=False).reset_index()
    address_issue_dataset_segments.rename(columns={0:'shipment_volume'},inplace=True)
    #observe - how the training data is spread - across each segment
    #address_issue_dataset_segments

    return address_issue_cat_preprocessed_final
#%%
    """
    #address_data.loc[address_data['']]
    #address_data.loc[((address_data['shipment_status']=='Delivered')&(address_data['attempts']>2))]
    later moddify address issue tags based on shipping attempts, status, tier, etc. - if needed
    """
#%%
#test autolabelling method - 
address_shipments_data_auto_labelled=label_by_attributes(address_shipments_data)
#%%
#sampling - for labelling - manually
def sampled_data_for_labelling(df):
        #sampling - training data to arrive at equal representation of each segment
        """
        sampling for equal representation of each combination when data segmented by 
        -> ndr status remark - with or without Address Issue Remark, 
        -> tier - 1,2,3 , 
        -> status - RTO, Delivered , 
        -> shipping attempts - 1, 2-3, >3
        """
        """
        for city in tier_2_lower:
            dataset_promise_merge.loc[dataset_promise_merge['city'].str.contains(city),'tier']=2
        """
        dataset_promise_merge=df.copy()
        print("delivered shipments in first attempt - identified with address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("delivered shipments with 2 or 3 attempts - identified with address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("delivered shipments with >3 attempts - identified with address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        
        
        print("RTO shipments in first attempt - identified with address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("RTO shipments with 2 or 3 attempts - identified with address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("RTO shipments with >3 attempts - identified with address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        
        
        print("delivered shipments in first attempt - identified with address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("delivered shipments with 2 or 3 attempts - identified with address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("delivered shipments with >3 attempts - identified with address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        
        
        print("RTO shipments in first attempt - identified with address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("RTO shipments with 2 or 3 attempts - identified with address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("RTO shipments with >3 attempts - identified with address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        print("delivered shipments in first attempt - identified with address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("delivered shipments with 2 or 3 attempts - identified with address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("delivered shipments with >3 attempts - identified with address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        
        
        print("RTO shipments in first attempt - identified with address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("RTO shipments with 2 or 3 attempts - identified with address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("RTO shipments with >3 attempts - identified with address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        #################3
        
        
        
        
        print("delivered shipments in first attempt - identified without address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("delivered shipments with 2 or 3 attempts - identified without address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("delivered shipments with >3 attempts - identified without address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        
        
        print("RTO shipments in first attempt - identified without address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("RTO shipments with 2 or 3 attempts - identified without address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("RTO shipments with >3 attempts - identified without address issue - in tier 1: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        
        
        print("delivered shipments in first attempt - identified without address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("delivered shipments with 2 or 3 attempts - identified without address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("delivered shipments with >3 attempts - identified without address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        
        
        print("RTO shipments in first attempt - identified without address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("RTO shipments with 2 or 3 attempts - identified without address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("RTO shipments with >3 attempts - identified without address issue - in tier 2: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        print("delivered shipments in first attempt - identified without address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("delivered shipments with 2 or 3 attempts - identified without address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("delivered shipments with >3 attempts - identified without address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        
        
        
        
        print("RTO shipments in first attempt - identified without address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))]))
        print("RTO shipments with 2 or 3 attempts - identified without address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))]))
        print("RTO shipments with >3 attempts - identified without address issue - in tier 3: ",len(dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))]))
        
        v1=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v2=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v3=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        
        
        v4=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v5=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v6=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        
        
        v7=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v8=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v9=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        
        
        v10=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v11=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v12=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        v13=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v14=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v15=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        
        
        v16=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v17=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v18=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']=='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        #################3
        
        
        
        
        v19=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v20=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v21=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        
        
        v22=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v23=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v24=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==1)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        
        
        v25=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v26=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v27=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        
        
        v28=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v29=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v30=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==2)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        v31=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v32=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v33=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='Delivered')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        
        
        
        
        v34=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']==1))].head(1500)
        v35=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>1)&(dataset_promise_merge['shipping_attempts']<=3))].head(1500)
        v36=dataset_promise_merge.loc[((dataset_promise_merge['lastNdrStatus']!='Address Issue')&(dataset_promise_merge['tier']==3)&(dataset_promise_merge['status']=='RTO')&(dataset_promise_merge['shipping_attempts']>3))].head(1500)
        
        v=pd.concat([v1,v2])
        
        v=pd.concat([v,v3])
        
        
        v=pd.concat([v,v4])
        v=pd.concat([v,v5])
        v=pd.concat([v,v6])
        v=pd.concat([v,v7])
        v=pd.concat([v,v8])
        v=pd.concat([v,v9])
        v=pd.concat([v,v10])
        v=pd.concat([v,v11])
        v=pd.concat([v,v12])
        
        v=pd.concat([v,v13])
        v=pd.concat([v,v14])
        v=pd.concat([v,v15])
        v=pd.concat([v,v16])
        v=pd.concat([v,v17])
        v=pd.concat([v,v18])
        v=pd.concat([v,v19])
        v=pd.concat([v,v20])
        v=pd.concat([v,v21])
        
        
        
        v=pd.concat([v,v22])
        v=pd.concat([v,v23])
        v=pd.concat([v,v24])
        v=pd.concat([v,v25])
        v=pd.concat([v,v26])
        v=pd.concat([v,v27])
        v=pd.concat([v,v28])
        v=pd.concat([v,v29])
        v=pd.concat([v,v30])
        
        
        
        
        v=pd.concat([v,v31])
        v=pd.concat([v,v32])
        v=pd.concat([v,v33])
        v=pd.concat([v,v34])
        v=pd.concat([v,v35])
        v=pd.concat([v,v36])
        address_to_label=v[['_id','end_desc_path','drop_location_customer_name','drop_location_phone','drop_location_pincode','zone','tier','shipping_attempts','lastNdrStatus','lastNdrDesc','ndr_desc_cat','drop_location_address','city','state','status','address_issue']]
        address_to_label['address_complete']=np.nan
        address_to_label.to_csv('address_label_raw_data.csv')
        return address_to_label
#%%