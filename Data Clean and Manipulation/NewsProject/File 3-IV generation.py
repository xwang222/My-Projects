# -*- coding: utf-8 -*-
"""
Created on Wed Jul 29 09:10:51 2020

@author: xwang222
"""

import pandas as pd
import random
import pdfplumber
import re
import ujson as json
from os import listdir
import os
import numpy as np
import nltk
import csv
import string
import calendar
import re
from datetime import datetime

##############################################################################
################################# prepare ####################################
each="IV.xlsx"
file_location="F:\\research projects\\Social Network\\Data\\IV"+ "\\" + each
df = pd.read_excel(file_location)
df.fillna(value=0, inplace=True)
name_list=df.columns
month=df['Series ID'].astype(str).tolist()
month_p=[]
for i in range(0,len(month)):
    key=month[i]
    y=key.split("-")[0]
    m=key.split("-")[1]
    
    ider=int(y)*100+int(m)
    month_p.append(ider)
    
Main=pd.DataFrame()
IV_out=pd.DataFrame()
start=month_p.index(201001)

##############################################################################
################################ contruct matrix #############################

for j in range(1,len(name_list)):
    #j=1141
    key=name_list[j]
    IV_dummy=[0]*252
    value=df[str(key)].values.tolist()
    
    # fixing -(N)
    for n in range(0,len(value)):
        val = value[n]
        if val =="-(N)":
            value[n]=value[n-1]
        else:
            pass
        
    threshold=[int(integral) for integral in value]
        
    dum_loc=[]
    for k in range(0,31):
        #k=0
        occurance=[i for i,d in enumerate(threshold) if d==k]
        occurance.insert(0,0)
        diff=np.diff(occurance)
        occur_2=[i for i,d in enumerate(diff) if d>=12]
        
        for each in occur_2:
            loc_2=occurance[each+1]
            dum_loc.append(loc_2)
        
        for i in range(0,len(dum_loc)):
            IV_dummy[dum_loc[i]]=1
        
    Main['month']=month_p
    Main['IV_dummy']=IV_dummy
    Main_2=Main.T
    new_header = Main_2.iloc[0] #grab the first row for the header
    Main_3 = Main_2[1:] #take the data less the header row
    Main_3.columns = new_header #set the header row as the df header
    Main_3.insert(0,"County", key)
    
    IV_out=pd.concat([IV_out, Main_3],sort=False)

##############################################################################
###################   slicing and take only periods after 2010 ###############
name_list_2=IV_out.columns
key2=name_list_2[start+1:]
key2=key2.insert(0,'County')
IV_ready=IV_out[key2]

CountyList = pd.read_csv(r"F:\research projects\Social Network\Data\CountyList.csv")
CountyList = CountyList.rename(columns={"name.1": "County"})
IV_ready_name=IV_ready.merge(CountyList,on="County",how="left")
IV_ready_name.to_csv('F:\\research projects\\Social Network\\Output\\IV_ready_0809.csv',index=False)

CountyList = CountyList['name'].values.tolist() 

##### augmented IV matrix  #####
AUG_IV = pd.DataFrame(columns = mon)

mon=month_p[156:]
test_1 = agent_month
test_1.fillna(value=9999, inplace=True)
name_list=test_1.columns.tolist()
list_2=name_list[3:]
test2=(test_1[list_2]<9990).astype(int)
test2['mon']=mon
test2=test2.set_index('mon')

test  = IV_ready.T
new_header = test.iloc[0] #grab the first row for the header
test1 = test[1:] #take the data less the header row
test1.columns = new_header #set the header row as the df header


code_key=[]
for i in range(0,len(list_2)):
    a=name_list_lk.index(list_2[i])
    b=code_list[a]
    code_key.append(b)

test3=test1[code_key]
test3.columns=list_2
test4=test3.mul(test2)
test4['row_sum'] = test4.sum(axis=1)
for i in range(0,len(list_2)):
    test4[list_2[i]] = np.where(test4['row_sum'] > 0, 1, test4[list_2[i]])

test4=test4.drop(columns=['row_sum'])
test5=test4.T
AUG_IV=pd.concat([AUG_IV, test5],sort=False)