# -*- coding: utf-8 -*-
"""
Created on Wed Apr 22 21:31:24 2020

@author: xwang222
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Apr 17 22:13:33 2020

@author: xwang222
"""

import pandas as pd
from pandas import ExcelWriter
from pandas import ExcelFile
import matplotlib.pyplot as plt
import numpy as np
#import statsmodels.api as sm
import glob
import os
#import matplotlib.dates as mdates

os.chdir('F:\\research projects\\Covid19\\test')                                # set work directory
#define a black dataframe
df_acc=pd.DataFrame()
df2_acc=pd.DataFrame()

for filepath in glob.iglob('F:\\research projects\\Project NRPS\\COVID-19\\csse_covid_19_data\\csse_covid_19_daily_reports/*.csv'): # read in all csv in the directory in loop
    df = pd.read_csv(filepath)                                                  # read in csv
    df=df.drop(['FIPS','Lat', 'Long_','Combined_Key','Country_Region'],axis=1)  # drop redundent column
    df.rename(columns = {'Admin2':'County'}, inplace = True)                    # rename county
    array1 = ['New York','Pennsylvania','Florida','Massachusetts','New Jersey','Connecticut','Maryland','District of Columbia']  # define the states you want
    df1=df[df['Province_State'].isin(array1)]                                   # filter the states you need
    #df1.drop(df1[df1['County'] == 'Unassigned'].index , inplace=True)          # drop unassigned value
    df1['Last_Update'].replace(':','',inplace=True)
    date_split=df1['Last_Update'].str.split(" ",n=1,expand=True)                # time format clean
    df1=df1.drop(['Last_Update'],axis=1)
    df1['Last_Update']=date_split[0]
    if df1['Last_Update'].str.contains("/").any()==True:                        # fix the time format
        date_split=df1['Last_Update'].str.split("/",n=2,expand=True)
        date_split[2]="2020"
        date_split[0]="0"+date_split[0]
        date_split[1]=pd.to_numeric(date_split[1])
        if date_split[1].mean()<10:
            date_split[1]='0'+date_split[1].astype(str)
          
        df1['Last_Update']=date_split[2]+"-"+date_split[0]+"-"+date_split[1].astype(str) 

    df_acc=df_acc.append(df1, ignore_index=True)                                # generate accumulated dataset
    
        
#df_acc.to_csv('UTD_Comb.csv')

#append data before from 310-322
    df2_acc=pd.DataFrame()
for filepath2 in glob.iglob('F:\\research projects\\Project NRPS\\COVID-19\\csse_covid_19_data\\csse_covid_19_daily_reports\\10-21/*.csv'): # read in all csv in the directory in loop
    df2 = pd.read_csv(filepath2)                                                # read in csv
    df2=df2.drop(['Latitude','Longitude', 'Country/Region'],axis=1)             # drop redundent column
    df2['Last Update'].replace(':','',inplace=True)
    date_split=df2['Last Update'].str.split("T",n=1,expand=True)
    df3=df2[df2['Province/State'].isin(array1)]
    df3=df3.drop(['Last Update'],axis=1)
    df3['Last Update']=date_split[0]
    df3.rename(columns = {'Last Update':'Last_Update'}, inplace = True)  
    df3.rename(columns = {'Province/State':'Province_State'}, inplace = True) 
    #df2.set_index('Last_Update',inplace = True)
    df2_acc=df2_acc.append(df3, ignore_index=True)
    #df2_acc.set_index('Last_Update',inplace = True)    
    #df2_acc.set_index('Last_Update')
#--------------------------------------------------------------------------------------------------------------------
NameList=['df_NY_County','df_PA_County','df_FL_County','df_MA_County','df_NJ_County','df_CT_County','df_MD_County','df_DC_County']
#FrameList=[df_NY_County,df_PA_County,df_FL_County,df_MA_County,df_NJ_County,df_CT_County,df_MD_County]
Abb=['NY','PA','FL','MA','NJ','CT','MD','DC']
StateList=['New York','Pennsylvania','Florida','Massachusetts','New Jersey','Connecticut','Maryland','District of Columbia']
i=0
while i < len(StateList):
    df_County=df_acc[df_acc['Province_State']==StateList[i]]                    # extract the county-level from acc
    df_10_21=df2_acc[df2_acc['Province_State']==StateList[i]]
    df_10_21=df_10_21.drop(['Province_State'],axis=1)
    df_10_21.set_index('Last_Update',inplace = True)
    df_State_Confirmed=df_County.groupby(['Last_Update'])['Confirmed'].sum()  # aggregate to state-level
    df_State_Deaths=df_County.groupby(['Last_Update'])['Deaths'].sum()
    df_State_Recovered=df_County.groupby(['Last_Update'])['Recovered'].sum()
    df_State_Active=df_County.groupby(['Last_Update'])['Active'].sum()
    df_State_Summary = pd.concat([df_State_Confirmed, df_State_Deaths,df_State_Recovered,df_State_Active], axis=1)
    df_State_Summary = df_State_Summary.append(df_10_21)
    df_State_Summary.sort_index(inplace = True)
    #df_CT_State_Summary['Confirm_lag']=df_CT_State_Summary['Confirmed'].shift(1)
    df_State_Summary['Daily_Increase_Confirm']=df_State_Summary['Confirmed']-df_State_Summary['Confirmed'].shift(1) # calculate data change
    df_State_Summary['Daily_Increase_Deaths']=df_State_Summary['Deaths']-df_State_Summary['Deaths'].shift(1)
    # if you want, you can also calculate second derivative
    
    m=i
    #plot
    #plt.style.use('ggplot')
    plt.figure(10*m)
    plt.grid(axis='both', alpha=.3)
    plt.plot(df_State_Summary['Deaths'])
    plt.xticks(df_State_Summary.index)
    plt.xticks(rotation=40)                        #, rotation='vertical'
    plt.title('Number of Death COVID-19 Cases in {}'.format(Abb[i]))
    plt.locator_params(nbins=10)
    plt.ylabel('Number of People Infected with COVID-19')
    plt.xlabel('Date')
    plt.gca().spines["top"].set_alpha(0.0)    
    plt.gca().spines["bottom"].set_alpha(0.3)
    plt.gca().spines["right"].set_alpha(0.0)    
    plt.gca().spines["left"].set_alpha(0.3)
    strFile = 'Accumulated_Deaths_{}.png'.format(Abb[i])
    if os.path.isfile(strFile):
        os.remove(strFile)   # Opt.: os.system("rm "+strFile)
    plt.savefig(strFile,bbox_inches='tight')
    
    #plt.style.use('ggplot')
    plt.figure(10*m+1)
    plt.grid(axis='both', alpha=.3)
    plt.plot(df_State_Summary['Confirmed'])
    plt.xticks(df_State_Summary.index)
    plt.xticks(rotation=40)                          #, rotation='vertical'
    plt.title('Number of Confirmed COVID-19 Cases in {}'.format(Abb[i]))
    plt.locator_params(nbins=10)
    plt.ylabel('Number of People Infected with COVID-19')
    plt.xlabel('Date')
    plt.gca().spines["top"].set_alpha(0.0)    
    plt.gca().spines["bottom"].set_alpha(0.3)
    plt.gca().spines["right"].set_alpha(0.0)    
    plt.gca().spines["left"].set_alpha(0.3)
    strFile = 'Accumulated_Confirm_{}.png'.format(Abb[i])
    if os.path.isfile(strFile):
        os.remove(strFile)   # Opt.: os.system("rm "+strFile)
    plt.savefig(strFile,bbox_inches='tight')
       
    index_test=list(range(0,len(df_County)))
    df_County.index = pd.RangeIndex(len(df_County.index))
    df_County.index = range(len(df_County.index))
    value=df_County['County']
    d={}
    n=0
    while n < len(value):
            d["{0}_summary".format(value[n])]=df_County[df_County['County']==value[n]]
            n=n+1
    for key in d:
        df_T=d[key]
        df_T.to_csv('F:\\research projects\\Covid19\\test\\{0}\\{1}_{2}.csv'.format(Abb[i],Abb[i],key))
    
    df_County.to_csv('F:\\research projects\\Covid19\\test\\{0}\\ALL_{1}_county.csv'.format(Abb[i],Abb[i]))
    i=i+1
#----------------------------------------------
