# -*- coding: utf-8 -*-
"""
Created on Sun Jul 26 22:01:10 2020

@author: xwang222
"""

# -*- coding: utf-8 -*-
"""
Created on Sun Jun 14 22:59:04 2020

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

# workflow
# File 1: generating sentiment matrix
#   step 1: pooling scraped news and combine them into a big dataframe (sentiment database)
#   step 2: constructing circulation matrix (coverage databse)
#   step 3: multiply step 1 and 2 (generate independent variable)
# File 2: generating outcome matrix
#   step 1: done with excel
# File 3: generating IV matrix
#   step 1:
# File 4: generating control variable matrix

CountyList = pd.read_csv(r"F:\research projects\Social Network\Data\CountyList.csv")
CountyList = CountyList['name'].values.tolist() 
column_names = CountyList
Main = pd.DataFrame(columns = column_names)
Main_blank = Main

each="name_code.xlsx"
file_location="F:\\research projects\\Social Network\\Data"+ "\\" + each
df2 = pd.read_excel(file_location)
name_list_lk=df2['name'].astype(str).tolist()
code_list=df2['code'].astype(str).tolist()

# obtain from file 3
test  = IV_ready.T
new_header = test.iloc[0] #grab the first row for the header
test1 = test[1:] #take the data less the header row
test1.columns = new_header #set the header row as the df header

################################################################################
################################################################################
# step 1: pooling scraped news and combine them into a big dataframe (sentiment database)
invalid_escape = re.compile(r'\\[0-7]{1,3}')  # up to 3 digits for byte values up to FF

def replace_with_byte(match):
    return chr(int(match.group(0)[1:], 8))

def repair(brokenjson):
    return invalid_escape.sub(replace_with_byte, brokenjson)

Newslist=[]
#Main=pd.DataFrame(Newslist)
#load data from json
File_List=listdir("F:\\research projects\\Social Network\\Data\\scraped News")
for each in File_List:
    news_location="F:\\research projects\\Social Network\\Data\\scraped News" + "\\" + each
    
    with open(news_location,encoding = "latin-1") as f:
      for jsonObj in f:
          studentDict = json.loads(repair(jsonObj))
          Newslist.append(studentDict)
          
df=pd.DataFrame(Newslist)

# remove exception and obituary
df_s1=df.loc[df['body']!="exception"]
df_s1=df_s1.loc[df_s1['date']!="exception"]
df_s1=df_s1.loc[pd.notna(df_s1['body'])]

# check if contain obituary
key1 = "obituar"
obit_list=[]
for i in range(0,len(df_s1)):
    #i=1723
    fullstring = df_s1.iloc[i]['body']
    if key1 in fullstring:
        x="yes"
    else:
        x="no"
    
    obit_list.append(x)

df_s1['ob']=obit_list
df_s2=df_s1.loc[df_s1['ob']=="no"]

# filter by year
year=[]
month=[]
date_list=df_s2['date'].values.tolist()
for i in range(0,len(date_list)):
    #i=0
    x = date_list[i]
    y=x.split(", ")[1]
    z=x.split(", ")[0]
    v=z.split(" ")[0]
    year.append(y)
    month.append(v)

df_s2=df_s2.reset_index()
df_s2=df_s2.drop(columns=['index'])
df_s2['year']=year
df_s2['month']=month
df_s3=df_s2.loc[(df_s2['year'].astype(int)<=2017) & (df_s2['year'].astype(int)>=2010)]
df_s3=df_s3.reset_index()
df_s3=df_s3.drop(columns=['index'])

'''
# export news body for preprocessing:
body_list = df_s3['body'].values.tolist()
body_list = [t.replace("</br></br>", " ") for t in body_list]
body_list = [t.replace("  ", " ") for t in body_list]
body_list = [re.sub(r'[^\x00-\x7F]+', ' ', t) for t in body_list]
body_list = [t.translate(str.maketrans('','',string.punctuation + string.digits)) for t in body_list]

predict_input =  pd.DataFrame(body_list)
predict_input.to_csv('F:\\research projects\\Social Network\\Output\\predict_0807.csv',index=False)
'''
predict_list = pd.read_csv(r"F:\research projects\Social Network\Data\rating_v2.csv")
temp = predict_list['positivity'].values.tolist()
df_s3['positivity']=temp # sent_base
del df_s2, df_s1

'''
source=df_s3['source'].values.tolist()
s_set=set(source)
s_unique = list(s_set)
AR_list=pd.DataFrame(s_unique)
AR_list.to_csv('F:\\research projects\\Social Network\\Output\\AR_list_0806.csv',index=False)
'''
########################################################################################
########################################################################################
# step 2: constructing circulation matrix (coverage databse)
# read in audit report
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
#######################################################################
#######################################################################
# step 3: multiply step 1 and 2
# create standardized matrix
ST=pd.DataFrame()
year=['2010','2011','2012','2013','2014','2015','2016','2017']
ST['year']=year
ST_month=pd.DataFrame(np.repeat(ST.values,12,axis=0))
ST_month.columns = ['year']
month_list=[]
N=int(len(ST_month)/12)
for h in range(0,N):
    for i in range(1,13):
      month_list.append(i)
ST_month['month']=month_list
ider_list=[]
year_list=ST_month['year'].values.tolist()
for i in range(0,len(ST_month)):
    ider=int(year_list[i])*100+month_list[i]
    ider_list.append(ider)
ST_month['ider']=ider_list

# create result matrix
column_names = CountyList
Result_main = pd.DataFrame(columns = column_names)

# step 3.1 generate identifier (source names don't match exactly)
key_list = pd.read_csv(r"F:\research projects\Social Network\Data\key_final.csv")
key_cvg = key_list['AAM'].values.tolist()
key_sent = key_list['NewsBank'].values.tolist()
from fuzzywuzzy import fuzz
match_key=[]
similarity_list=[]
for i in range(0,len(key_cvg)):
    #i=6
    #print(i)
    key = key_cvg[i]
    similarity_list=[]
    #key = s_unique[i]
    for k in range(0,len(unique_name_history)):
        #k=11
               
        match_text=unique_name_history[k]
        
        text_similarity=fuzz.ratio(key, match_text)
        similarity_list.append(text_similarity) 
    
    j = similarity_list.index(max(similarity_list))
    key_m=unique_name_history[j]
    match_key.append(key_m)

# step 3.2 multiplication
for i in range(0,len(key_sent)):
    #i=6
    print(i)
    key1=key_sent[i]
    key2=match_key[i]
    
    # extract from pooled news
    temp1=df_s3[df_s3['source']==key1]
    
    year=[]
    month=[]
    ider=[]
    date_list=temp1['date'].values.tolist()
    for i in range(0,len(date_list)):
        #i=0
        x = str(date_list[i])
        y=x.split(", ")[1]
        z=x.split(", ")[0]
        v=z.split(" ")[0]
        year.append(y)
        month.append(v)
        
    month=[word.replace('January','1') for word in month]
    month=[word.replace('February','2') for word in month]     
    month=[word.replace('March','3') for word in month]
    month=[word.replace('April','4') for word in month]     
    month=[word.replace('May','5') for word in month]
    month=[word.replace('June','6') for word in month]     
    month=[word.replace('July','7') for word in month]
    month=[word.replace('August','8') for word in month]     
    month=[word.replace('September','9') for word in month]
    month=[word.replace('October','10') for word in month]     
    month=[word.replace('November','11') for word in month]
    month=[word.replace('December','12') for word in month]     

    for j in range(0,len(date_list)):
        y=year[j]
        v=month[j]
        u=int(y)*100+int(v)
        ider.append(u)
        
    temp1=temp1.reset_index()
    temp1=temp1.drop(columns=['index'])
    temp1['year']=year
    temp1['month']=month
    temp1['ider']=ider
    
    temp1_v2=temp1.groupby(['ider'])['positivity'].mean()
    temp1_v2=temp1_v2.reset_index()                        #ready to map
    # map into standized matrix
    ST_m=ST_month.merge(temp1_v2,on="ider",how="left")     ## ready to multiply with circulation matrix
    A=ST_m[['ider','positivity']]
    A=A.set_index('ider')

    
    # extract from circulation matrix
    #key2="KANSAS CITY STAR"
    temp2 = Main_1[Main_1['name']==key2]
    B=temp2.loc[(temp2['year'].astype(int)<=2017) & (temp2['year'].astype(int)>=2010)]
    test1=B.sum()
    B=B.reset_index() 
    list1=B['year']
    list2=B['month']
    ider=[]
    for i in range(0,len(list1)):
        u=list1[i]
        v=list2[i]
        w=int(u)*100+int(v)
        
        ider.append(w)
    
    B.insert(2,"ider", ider)
    B=B.sort_values(by=['ider'])
    B=B.reset_index()
    B=B.set_index('ider')
    B=B.drop(columns=['year','level_0','index','name','year','month'])
    
    func = lambda x: np.asarray(x) * np.asarray(A['positivity'])    
    result=B.apply(func)

    Result_main=pd.concat([Result_main, result],sort=False)

# step 3.3 clean and check
#   3.3.1 remove NaN
Result_main.fillna(value=0, inplace=True)
Result_main=Result_main.reset_index()
Result_main=Result_main.drop(columns=['year','name','month'])

Result_main_v2=Result_main.groupby(['index']).sum()
test1=Result_main_v2.sum()

#   3.3.2 generate local sentiment
RAW_SENT = Result_main_v2.T  # this is the matrix for sentiment of each county
df_rs=pd.DataFrame(RAW_SENT)
df_rs.to_csv('F:\\research projects\\Social Network\\Output\\sent_v1.csv',index=True)
#   3.3.3 Apply social network weight


print ("independent generating process finished")
######################## independent generating process finished ###############


