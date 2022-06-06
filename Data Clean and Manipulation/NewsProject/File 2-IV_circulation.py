# -*- coding: utf-8 -*-
"""
Created on Mon Apr  5 19:17:56 2021

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

CountyList = pd.read_csv(r"F:\research projects\Social Network\Data\CountyList.csv")
CountyList = CountyList['name'].values.tolist() 
column_names = CountyList

Main = pd.DataFrame(columns = column_names)
unique_name_history=[]
unique_name_history_l=[]
File_List=listdir(r"F:\research projects\Social Network\Data\AR")
for each in File_List:
    #each="ST. LOUIS AMERICAN.xlsx"
    ar_location="F:\\research projects\\Social Network\\Data\\AR"+ "\\" + each
    AR_test = pd.read_excel(ar_location)
    AR_test_2=AR_test.drop(index=0)
    new_header = AR_test_2.iloc[0] #grab the first row for the header
    AR_test_3 = AR_test_2[1:] #take the data less the header row
    AR_test_3.columns = new_header #set the header row as the df header
    AR_test_3=AR_test_3.reset_index()
    AR_test_3=AR_test_3.drop(columns=['index'])
    AR_test_3['County Name'] = AR_test_3['County Name'].str.upper()
    AR_test_3['County Name'] = AR_test_3['County Name'].str.replace('ST. ','ST.')
    # replace state name with abbreviation
    AR_test_3['State of County'].replace("ALABAMA", "AL",inplace=True)
    AR_test_3['State of County'].replace("ALASKA", "AK",inplace=True)
    AR_test_3['State of County'].replace("ARIZONA", "AZ",inplace=True)
    AR_test_3['State of County'].replace("ARKANSAS", "AR",inplace=True)
    AR_test_3['State of County'].replace("CALIFORNIA", "CA",inplace=True)
    AR_test_3['State of County'].replace("COLORADO", "CO",inplace=True)
    AR_test_3['State of County'].replace("CONNECTICUT", "CT",inplace=True)
    AR_test_3['State of County'].replace("DELAWARE", "DE",inplace=True)
    AR_test_3['State of County'].replace("FLORIDA", "FL",inplace=True)
    AR_test_3['State of County'].replace("GEORGIA", "GA",inplace=True)
    AR_test_3['State of County'].replace("HAWAII", "HI",inplace=True)
    AR_test_3['State of County'].replace("IDAHO", "ID",inplace=True)
    AR_test_3['State of County'].replace("ILLINOIS", "IL",inplace=True)
    AR_test_3['State of County'].replace("INDIANA", "IN",inplace=True)
    AR_test_3['State of County'].replace("IOWA", "IA",inplace=True)
    AR_test_3['State of County'].replace("KANSAS", "KS",inplace=True)
    AR_test_3['State of County'].replace("KENTUCKY", "KY",inplace=True)
    AR_test_3['State of County'].replace("LOUISIANA", "LA",inplace=True)
    AR_test_3['State of County'].replace("MAINE", "ME",inplace=True)
    AR_test_3['State of County'].replace("MARYLAND", "MD",inplace=True)
    AR_test_3['State of County'].replace("MASSACHUSETTS", "MA",inplace=True)
    AR_test_3['State of County'].replace("MICHIGAN", "MI",inplace=True)
    AR_test_3['State of County'].replace("MINNESOTA", "MN",inplace=True)
    AR_test_3['State of County'].replace("MISSISSIPPI", "MS",inplace=True)
    AR_test_3['State of County'].replace("MISSOURI", "MO",inplace=True)
    AR_test_3['State of County'].replace("MONTANA", "MT",inplace=True)
    AR_test_3['State of County'].replace("NEBRASKA", "NE",inplace=True)
    AR_test_3['State of County'].replace("NEVADA", "NV",inplace=True)
    AR_test_3['State of County'].replace("NEW HAMPSHIRE", "NH",inplace=True)
    AR_test_3['State of County'].replace("NEW JERSEY", "NJ",inplace=True)
    AR_test_3['State of County'].replace("NEW MEXICO", "NM",inplace=True)
    AR_test_3['State of County'].replace("NEW YORK", "NY",inplace=True)
    AR_test_3['State of County'].replace("NORTH CAROLINA", "NC",inplace=True)
    AR_test_3['State of County'].replace("NORTH DAKOTA", "ND",inplace=True)
    AR_test_3['State of County'].replace("OHIO", "OH",inplace=True)
    AR_test_3['State of County'].replace("OKLAHOMA", "OK",inplace=True)
    AR_test_3['State of County'].replace("OREGON", "OR",inplace=True)
    AR_test_3['State of County'].replace("PENNSYLVANIA", "PA",inplace=True)
    AR_test_3['State of County'].replace("RHODE ISLAND", "RI",inplace=True)
    AR_test_3['State of County'].replace("SOUTH CAROLINA", "SC",inplace=True)
    AR_test_3['State of County'].replace("SOUTH DAKOTA", "SD",inplace=True)
    AR_test_3['State of County'].replace("TENNESSEE", "TN",inplace=True)
    AR_test_3['State of County'].replace("TEXAS", "TX",inplace=True)
    AR_test_3['State of County'].replace("UTAH", "UT",inplace=True)
    AR_test_3['State of County'].replace("VERMONT", "VT",inplace=True)
    AR_test_3['State of County'].replace("VIRGINIA", "VA",inplace=True)
    AR_test_3['State of County'].replace("WASHINGTON", "WA",inplace=True)
    AR_test_3['State of County'].replace("WEST VIRGINIA", "WV",inplace=True)
    AR_test_3['State of County'].replace("WISCONSIN", "WI",inplace=True)
    AR_test_3['State of County'].replace("WYOMING", "WY",inplace=True)
    AR_test_3['State of County'].replace("District of Columbia", "DC",inplace=True)
    AR_test_3['State of County'].replace("Marshall Islands", "MH",inplace=True)
    
    #AR_test_3['County Name'].replace("DE WITT", "DEWITT",inplace=True)
    AR_test_3['County Name'].replace("ST. CLAIR", "ST.CLAIR",inplace=True)
    AR_test_3['County Name'].replace("McDONALD", "MCDONALD",inplace=True)
    AR_test_3['County Name'].replace("BEDFORD CITY", "BEDFORD",inplace=True)
    AR_test_3['County Name'].replace("McKEAN", "MCKEAN",inplace=True)
    AR_test_3['County Name'].replace("McDOWELL", "MCDOWELL",inplace=True)
    AR_test_3['County Name'].replace("LA SALLE", "LASALLE",inplace=True)
    AR_test_3['County Name'].replace("McPHERSON", "MCPHERSON",inplace=True)
    AR_test_3['County Name'].replace("McINTOSH", "MCINTOSH",inplace=True)
    AR_test_3['County Name'].replace("McKINLEY", "MCKINLEY",inplace=True)
    AR_test_3['County Name'].replace("ST. FRANCIS", "ST.FRANCIS",inplace=True)
    AR_test_3['County Name'].replace("ST. CROIX", "ST.CROIX",inplace=True)
    AR_test_3['County Name'].replace("ACADIA", "ACADIA PARISH",inplace=True)
    AR_test_3['County Name'].replace("ALLEN", "ALLEN PARISH",inplace=True)
    AR_test_3['County Name'].replace("BEAUREGARD", "BEAUREGARD PARISH",inplace=True)
    AR_test_3['County Name'].replace("CALCASIEU", "CALCASIEU PARISH",inplace=True)
    AR_test_3['County Name'].replace("CAMERON", "CAMERON PARISH",inplace=True)
    AR_test_3['County Name'].replace("JEFFERSON DAVIS", "JEFFERSON DAVIS PARISH",inplace=True)
    AR_test_3['County Name'].replace("VERMILION", "VERMILION PARISH",inplace=True)
    AR_test_3['County Name'].replace("VERNON", "VERNON PARISH",inplace=True)
    AR_test_3['County Name'].replace("EVANGELINE", "EVANGELINE PARISH",inplace=True)
    AR_test_3['County Name'].replace("BOSSIER", "BOSSIER PARISH",inplace=True)
    AR_test_3['County Name'].replace("CADDO", "CADDO PARISH",inplace=True)
    AR_test_3['County Name'].replace("BUENA VIST.CITY", "BUENA VISTA CITY",inplace=True)
    AR_test_3['County Name'].replace("LA PORTE", "LAPORTE",inplace=True)
    AR_test_3['County Name'].replace("CLIFTON FORGE CITY", "ALLEGHANY",inplace=True)
    AR_test_3['County Name'].replace('SAINT HELENA','ST.HELENA PARISH',inplace=True)
    AR_test_3['County Name'].replace('SAINT JAMES','ST.JAMES PARISH',inplace=True)
    AR_test_3['County Name'].replace('SAINT LANDRY','ST.LANDRY PARISH',inplace=True)
    AR_test_3['County Name'].replace('SAINT MARTIN','ST.MARTIN PARISH',inplace=True)
    AR_test_3['County Name'].replace('SAINT MARY','ST.MARY PARISH',inplace=True)

    #AR_test_3['County Name'].replace('PLAQUEMINES','PLAQUEMINES PARISH',inplace=True)
    AR_test_3['County Name'].replace('SAINT BERNARD','ST.BERNARD PARISH',inplace=True)
    AR_test_3['County Name'].replace('SAINT CHARLES','ST.CHARLES PARISH',inplace=True)
    AR_test_3['County Name'].replace('SAINT JOHN THE BAPTIST','ST.JOHN THE BAPTIST PARISH',inplace=True)
    AR_test_3['County Name'].replace('SAINT TAMMANY','ST.TAMMANY PARISH',inplace=True)

   
    
    AR_test_3['Reporting Cycle'].replace("BI", 2,inplace=True)
    AR_test_3['Reporting Cycle'].replace("AN", 1,inplace=True)
    #AR_test_3['Reporting Cycle']=AR_test_3['Reporting Cycle'].astype(int)
    # combine state and county name
    AR_test_3['loc']=AR_test_3['County Name']+',' + AR_test_3['State of County']
    
    AR_test_3['loc'].replace("ALLEN PARISH,IN", "ALLEN,IN",inplace=True)
    AR_test_3['loc'].replace("CADDO PARISH,OK", "CADDO,OK",inplace=True)
    AR_test_3['loc'].replace("CAMERON PARISH,TX", "CAMERON,TX",inplace=True)
    AR_test_3['loc'].replace("VERMILION PARISH,IL", "VERMILION,IL",inplace=True)
    AR_test_3['loc'].replace("CAMERON PARISH,PA", "CAMERON,PA",inplace=True)
    AR_test_3['loc'].replace("STE. GENEVIEVE,MO", "STE.GENEVIEVE,MO",inplace=True)    
    AR_test_3['loc'].replace("LASALLE,TX", "LA SALLE,TX",inplace=True)       
    AR_test_3['loc'].replace("DEWITT,IL", "DE WITT,IL",inplace=True)
    AR_test_3['loc'].replace("ALLEN PARISH,OH", "ALLEN,OH",inplace=True)
    AR_test_3['loc'].replace("VERNON PARISH,MO", "VERNON,MO",inplace=True)
    AR_test_3['loc'].replace("ALLEN PARISH,KS", "ALLEN,KS",inplace=True)
    AR_test_3['loc'].replace("VERNON PARISH,WI", "VERNON,WI",inplace=True)
    AR_test_3['loc'].replace("DISTRICT OF COLUMBIA,DISTRICT OF COLUMBIA", "DISTRICT OF COLUMBIA    ,DC",inplace=True)
    AR_test_3['loc'].replace("SHANNON,SD", "OGLALA LAKOTA,SD",inplace=True)
    AR_test_3['loc'].replace('ASCENSION,LA','ASCENSION PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'ASSUMPTION,LA', 'ASSUMPTION PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'AVOYELLES,LA', 'AVOYELLES PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'EAST BATON ROUGE,LA', 'EAST BATON ROUGE PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'EAST FELICIANA,LA', 'EAST FELICIANA PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'IBERIA,LA', 'IBERIA PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'IBERVILLE,LA', 'IBERVILLE PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'LAFAYETTE,LA', 'LAFAYETTE PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'LAFOURCHE,LA', 'LAFOURCHE PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'LIVINGSTON,LA', 'LIVINGSTON PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'POINTE COUPEE,LA', 'POINTE COUPEE PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'RAPIDES,LA', 'RAPIDES PARISH,LA',inplace=True) 
        
    AR_test_3['loc'].replace( 'TANGIPAHOA,LA', 'TANGIPAHOA PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'WEST BATON ROUGE,LA', 'WEST BATON ROUGE PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'WEST FELICIANA,LA', 'WEST FELICIANA PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'JEFFERSON,LA', 'JEFFERSON PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'ORLEANS,LA', 'ORLEANS PARISH,LA',inplace=True)
    AR_test_3['loc'].replace( 'PLAQUEMINES,LA', 'PLAQUEMINES PARISH,LA',inplace=True)

    AR_test_3['loc'].replace( 'TERREBONNE,LA', 'TERREBONNE PARISH,LA',inplace=True)

    #AR_test_3['loc'].replace("MATANUSKA", "MATANUSKA-SUSITNA,AK",inplace=True) 
    #AR_test_3['loc'].replace("VALDEZ", "VALDEZ-CORDOVA,AK",inplace=True)       
    
    AR_test_3=AR_test_3.loc[pd.notna(AR_test_3['% of Household Coverage'])]
    AR_test_4=AR_test_3[['Member Name','Reporting Cycle','Reporting Date','Standard Frequency','loc','% of Household Coverage']]
    AR_test_4=AR_test_4.reset_index()
    AR_test_4=AR_test_4.drop(columns=['index'])
    
    Member_Name=AR_test_4['Member Name'].values.tolist()
    #rep_fre=AR_test_4['Reporting Cycle'].values.tolist()
    M_set=set(Member_Name)
    M_unique = list(M_set)
    num_M_uniq=len(M_unique)
    unique_name_history_l.append(num_M_uniq)
    name=M_unique[0]
    #rep_fre_set=set(rep_fre)
    #rep_uniq=list(rep_fre_set)
    #rep_fre=rep_uniq[0]
    unique_name_history.append(name)
    # generate year of AR
    year=[]
    date_list=AR_test_4['Reporting Date'].values.tolist()
    for i in range(0,len(date_list)):
        #i=0
        x = str(date_list[i])
        y=x.split("-")[0]
        year.append(y)
    
    # generate id because different frequency
    AR_test_4['year']=year
    AR_test_4['id']=AR_test_4['year']+'~' + AR_test_4['loc']
    AR_test_4['% of Household Coverage'] = AR_test_4['% of Household Coverage'].astype(float)
    AR_test_5=AR_test_4.groupby(['id']).mean()
    AR_test_5=AR_test_5.reset_index()
    
    year=[]
    loc=[]
    id_list=AR_test_5['id'].values.tolist()
    for i in range(0,len(id_list)):
        #i=0
        x = str(id_list[i])
        y=x.split("~")[0]
        z=x.split("~")[1]
        year.append(y)
        loc.append(z)
    
    AR_test_5['year']=year
    AR_test_5['loc']=loc
    AR_test_5=AR_test_5.drop(columns=['id'])
    del AR_test_4, AR_test_3, AR_test_2
    
    # reshape data frame by year and stack
    period=['2010','2011','2012','2013','2014','2015','2016','2017']
    year=AR_test_5['year'].values.tolist()
    year_set=set(year)
    year_unique = list(year_set)
    agent_main=pd.DataFrame()
    rep_fre=AR_test_5['Reporting Cycle']
    for i in year_unique:
        #i=2012
        
        aux_1=AR_test_5.loc[AR_test_5['year']==str(i)]
        rep_fre=int(sum(list(set(aux_1['Reporting Cycle'])))/len(list(set(aux_1['Reporting Cycle']))))
        aux_2=aux_1[['loc','% of Household Coverage']]
        aux_3 = aux_2.T
        new_header = aux_3.iloc[0] #grab the first row for the header
        aux_4 = aux_3[1:] #take the data less the header row
        aux_4.columns = new_header #set the header row as the df header
        aux_4=aux_4.reset_index()
        aux_4=aux_4.drop(columns=[1])
        year=[str(i)]
        aux_4.insert(0,"year", year)
        aux_4.insert(0,"name", name)
        
        agent_main=pd.concat([agent_main, aux_4],sort=False)   # reporting year
        
        if rep_fre==2: 
            aux_4=aux_4.drop(columns=['year'])
            year=[int(i)-1]
            aux_4.insert(0,"year", year)
            #aux_4.insert(0,"name", name)
            
            agent_main=pd.concat([agent_main, aux_4],sort=False)   # one year before
        
        else:
            pass
    
    year_check=agent_main['year'].values.tolist()
    year_check = list(map(int, year_check))
    #year_check_set=set(year_check)
    min_year=min(year_check)
    max_year=max(year_check)
    
    if min_year>2010:
        diff=min_year-2010
        for i in range(0,diff):
            #i=0
            test=agent_main.loc[agent_main['year'].astype(int)==min_year]
            test=test.drop(columns=['year'])
            year=[min_year-i-1]
            test.insert(0,"year", year)
            
            agent_main=pd.concat([agent_main, test],sort=False)
    else:
        pass
    
    if max_year<2017:
        diff=2017-max_year
        for i in range(0,diff):
            test=agent_main.loc[agent_main['year'].astype(int)==max_year]
            test=test.drop(columns=['year'])
            year=[max_year+i+1]
            test.insert(0,"year", year)
            
            agent_main=pd.concat([agent_main, test],sort=False)
    else:
        pass
    
    year_check_2=agent_main['year'].values.tolist()
    year_check_2 = list(map(int, year_check_2))
    year_check_set=set(year_check_2)
    period_2=[2010,2011,2012,2013,2014,2015,2016,2017]
    complete=set(period_2)
    Missing_year=complete.difference(year_check_set)
    Missing_year=list(Missing_year)
    
    if len(Missing_year)!=0:
        #print("detected")
        for i in reversed(range(0,len(Missing_year))):
            missing=Missing_year[i]
            test=agent_main.loc[agent_main['year'].astype(int)==missing+1]
            test=test.drop(columns=['year'])
            year=[missing]
            test.insert(0,"year", year)
                
            agent_main=pd.concat([agent_main, test],sort=False)
    else:
        pass
    
    year_check_2=agent_main['year'].values.tolist()
    year_check_2 = list(map(int, year_check_2))
    year_check_set=set(year_check_2)
    period_2=[2010,2011,2012,2013,2014,2015,2016,2017]
    complete=set(period_2)
    Missing_year=complete.difference(year_check_set)
    Missing_year=list(Missing_year)
    
    if len(Missing_year)!=0:
        print("detected"+each)
        
    
    col_name=list(agent_main.columns)
    agent_month=pd.DataFrame(np.repeat(agent_main.values,12,axis=0))
    agent_month.columns = col_name
    month_list=[]
    N=int(len(agent_month)/12)
    for h in range(0,N):
        for i in range(1,13):
          month_list.append(i)
    
    agent_month.insert(2,"month", month_list)
    
    A=len(Main.columns.tolist())
    
    Main=pd.concat([Main, agent_month],sort=False)
      
    if len(Main.columns.tolist())>A:
        print(name)
    
    
    #augment IV
    
    
County_list_2=Main.columns.tolist()
Main_1=Main.iloc[:,:-11]
Main_1.fillna(value=0, inplace=True)
test2=Main_1.sum()
test1=list(Main_1.sum())
test1.count(0)
Main_1.to_csv('F:\\research projects\\Social Network\\Output\\circulation_0405.csv',index=False)

##############################################################################
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