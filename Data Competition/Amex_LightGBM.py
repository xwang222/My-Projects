# -*- coding: utf-8 -*-
"""
Created on Mon Sep  5 18:51:23 2022

@author: xwang222
"""
# -*- coding: utf-8 -*-
"""
Created on Sun Aug 21 08:32:51 2022

@author: xwang222
"""
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 18 14:27:23 2022

@author: xwang222
"""
import gc
import os
import joblib
import random
import warnings
import itertools
import scipy as sp
import numpy as np
import pandas as pd
from tqdm import tqdm
import lightgbm as lgb
from itertools import combinations
pd.set_option('display.width', 1000)
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
from sklearn.preprocessing import LabelEncoder
import warnings; warnings.filterwarnings('ignore')
from sklearn.model_selection import StratifiedKFold, train_test_split

class CFG:
    seed = 42
    n_folds = 3
    target = 'target'
    input_dir = 'C:/Users/xwang222/Downloads/Amex/'

def get_difference(data, num_features):
    df1 = []
    customer_ids = []
    for customer_id, df in tqdm(data.groupby(['customer_ID'])):
        diff_df1 = df[num_features].diff(1).iloc[[-1]].values.astype(np.float32)
        df1.append(diff_df1)
        customer_ids.append(customer_id)
    df1 = np.concatenate(df1, axis = 0)
    df1 = pd.DataFrame(df1, columns = [col + '_diff1' for col in df[num_features].columns])
    df1['customer_ID'] = customer_ids
    return df1

def read_preprocess_data():
    train = pd.read_parquet('../input/amex-data-integer-dtypes-parquet-format/train.parquet')
    features = train.drop(['customer_ID', 'S_2'], axis = 1).columns.to_list()
    cat_features = [
        "B_30",
        "B_38",
        "D_114",
        "D_116",
        "D_117",
        "D_120",
        "D_126",
        "D_63",
        "D_64",
        "D_66",
        "D_68",
    ]
    num_features = [col for col in features if col not in cat_features]
    print('Starting training feature engineer...')
    train_num_agg = train.groupby("customer_ID")[num_features].agg(['first', 'mean', 'std', 'min', 'max', 'last'])
    train_num_agg.columns = ['_'.join(x) for x in train_num_agg.columns]
    train_num_agg.reset_index(inplace = True)

    # Lag Features
    for col in train_num_agg:
        if 'last' in col and col.replace('last', 'first') in train_num_agg:
            train_num_agg[col + '_lag_sub'] = train_num_agg[col] - train_num_agg[col.replace('last', 'first')]
            train_num_agg[col + '_lag_div'] = train_num_agg[col] / train_num_agg[col.replace('last', 'first')]

    train_cat_agg = train.groupby("customer_ID")[cat_features].agg(['count', 'first', 'last', 'nunique'])
    train_cat_agg.columns = ['_'.join(x) for x in train_cat_agg.columns]
    train_cat_agg.reset_index(inplace = True)
    
    train_labels = pd.read_csv('../input/amex-default-prediction/train_labels.csv')
    # Transform float64 columns to float32
    cols = list(train_num_agg.dtypes[train_num_agg.dtypes == 'float64'].index)
    for col in tqdm(cols):
        train_num_agg[col] = train_num_agg[col].astype(np.float32)
    # Transform int64 columns to int32
    cols = list(train_cat_agg.dtypes[train_cat_agg.dtypes == 'int64'].index)
    for col in tqdm(cols):
        train_cat_agg[col] = train_cat_agg[col].astype(np.int32)
    # Get the difference
    train_diff = get_difference(train, num_features)
    train = train_num_agg.merge(train_cat_agg, how = 'inner', on = 'customer_ID').merge(train_diff, how = 'inner', on = 'customer_ID').merge(train_labels, how = 'inner', on = 'customer_ID')
    del train_num_agg, train_cat_agg, train_diff
    gc.collect()
    
    # Test FE
    test = pd.read_parquet('../input/amex-data-integer-dtypes-parquet-format/test.parquet')
    print('Starting test feature engineer...')
    test_num_agg = test.groupby("customer_ID")[num_features].agg(['first', 'mean', 'std', 'min', 'max', 'last'])
    test_num_agg.columns = ['_'.join(x) for x in test_num_agg.columns]
    test_num_agg.reset_index(inplace = True)

    # Lag Features
    for col in test_num_agg:
        if 'last' in col and col.replace('last', 'first') in test_num_agg:
            test_num_agg[col + '_lag_sub'] = test_num_agg[col] - test_num_agg[col.replace('last', 'first')]
            test_num_agg[col + '_lag_div'] = test_num_agg[col] / test_num_agg[col.replace('last', 'first')]

    test_cat_agg = test.groupby("customer_ID")[cat_features].agg(['count', 'first', 'last', 'nunique'])
    test_cat_agg.columns = ['_'.join(x) for x in test_cat_agg.columns]
    test_cat_agg.reset_index(inplace = True)
    # Transform float64 columns to float32
    cols = list(test_num_agg.dtypes[test_num_agg.dtypes == 'float64'].index)
    for col in tqdm(cols):
        test_num_agg[col] = test_num_agg[col].astype(np.float32)
    # Transform int64 columns to int32
    cols = list(test_cat_agg.dtypes[test_cat_agg.dtypes == 'int64'].index)
    for col in tqdm(cols):
        test_cat_agg[col] = test_cat_agg[col].astype(np.int32)
    # Get the difference
    test_diff = get_difference(test, num_features)
    test = test_num_agg.merge(test_cat_agg, how = 'inner', on = 'customer_ID').merge(test_diff, how = 'inner', on = 'customer_ID')
    del test_num_agg, test_cat_agg, test_diff
    gc.collect()
    # Save files to disk

    train.to_parquet('train_fe_plus_plus.parquet')
    test.to_parquet('test_fe_plus_plus.parquet')
    
# Read & Preprocess Data
# read_preprocess_data()

def Create_S_2_D_39_tr():
    train = pd.read_parquet('C:/Users/xwang222/Downloads/Amex/train.parquet',columns=['customer_ID','S_2','D_39'])
    train['S_2'] = pd.to_datetime(train['S_2'])
    train['month'] = pd.DatetimeIndex(train['S_2']).month
    shifted = train.groupby(['customer_ID'])['month'].shift(-1)
    train=train.join(shifted.rename("month_lag"))
    train['diff']=train['month_lag']-train['month']
    train['ever_gap']=0
    train['ever_gap_D39']=0
    train.loc[(train["diff"] != 1) & (train["diff"] != -11) & (train["diff"].isnull()==False), "ever_gap"] = 1
    train.loc[(train["ever_gap"] == 1) & (train["D_39"] >= 120), "ever_gap_D39"] = 1
    V1=train.groupby(['customer_ID'])["ever_gap_D39"].max()
    V1 = V1.reset_index() 
    V2=train.groupby(['customer_ID'])["ever_gap_D39"].sum()
    V2=V2.reset_index()
    id_list=train['customer_ID'].unique()
    df_EM_tr=pd.DataFrame(id_list)
    df_EM_tr=df_EM_tr.rename(columns={0: "customer_ID"})
    df_EM_tr= df_EM_tr.merge(V1, how = 'inner', on = 'customer_ID').merge(V2, how = 'inner', on = 'customer_ID')
    return df_EM_tr

def Create_S_2_D_39_ts():
    test = pd.read_parquet('C:/Users/xwang222/Downloads/Amex/test.parquet',columns=['customer_ID','S_2','D_39'])
    test['S_2'] = pd.to_datetime(test['S_2'])
    test['month'] = pd.DatetimeIndex(test['S_2']).month
    shifted = test.groupby(['customer_ID'])['month'].shift(-1)
    test=test.join(shifted.rename("month_lag"))
    test['diff']=test['month_lag']-test['month']
    test['ever_gap']=0
    test['ever_gap_D39']=0
    test.loc[(test["diff"] != 1) & (test["diff"] != -11) & (test["diff"].isnull()==False), "ever_gap"] = 1
    test.loc[(test["ever_gap"] == 1) & (test["D_39"] >= 120), "ever_gap_D39"] = 1
    V1=test.groupby(['customer_ID'])["ever_gap_D39"].max()
    V1 = V1.reset_index() 
    V2=test.groupby(['customer_ID'])["ever_gap_D39"].sum()
    V2=V2.reset_index()
    id_list=test['customer_ID'].unique()
    df_EM_ts=pd.DataFrame(id_list)
    df_EM_ts=df_EM_ts.rename(columns={0: "customer_ID"})
    df_EM_ts= df_EM_ts.merge(V1, how = 'inner', on = 'customer_ID').merge(V2, how = 'inner', on = 'customer_ID')
    return df_EM_ts

def iv_woe(data, target, bins=20, show_woe=False):
    
    #Empty Dataframe
    newDF,woeDF = pd.DataFrame(), pd.DataFrame()
    
    #Extract Column Names
    cols = data.columns
    
    #Run WOE and IV on all the independent variables
    for ivars in cols[~cols.isin([target])]:

        print(ivars)

        if (data[ivars].dtype.kind in 'bifc') and (len(np.unique(data[ivars]))>3):
            binned_x = pd.qcut(data[ivars], bins,  duplicates='drop')
            d0 = pd.DataFrame({'x': binned_x, 'y': data[target]})
        else:
            d0 = pd.DataFrame({'x': data[ivars], 'y': data[target]})
            
        d0 = d0.astype({"x": str})
        d = d0.groupby("x", as_index=False, dropna=False).agg({"y": ["count", "sum"]})
        d.columns = ['Cutoff', 'N', 'Events']
        d['% of Events'] = np.maximum(d['Events'], 0.5) / d['Events'].sum()
        d['Non-Events'] = d['N'] - d['Events']
        d['% of Non-Events'] = np.maximum(d['Non-Events'], 0.5) / d['Non-Events'].sum()
        d['WoE'] = np.log(d['% of Non-Events']/d['% of Events'])
        d['IV'] = d['WoE'] * (d['% of Non-Events']-d['% of Events'])
        d.insert(loc=0, column='Variable', value=ivars)
        print("Information value of " + ivars + " is " + str(round(d['IV'].sum(),6)))
        temp =pd.DataFrame({"Variable" : [ivars], "IV" : [d['IV'].sum()]}, columns = ["Variable", "IV"])
        newDF=pd.concat([newDF,temp], axis=0)
        woeDF=pd.concat([woeDF,d], axis=0)

        #Show WOE Table
        if show_woe == True:
            print(d)
    return newDF, woeDF

def non_linar_tr():
    high=['P_2', 'D_48', 'R_1', 'S_3', 'B_7']
    # read only categorial  features
    data = pd.read_parquet('C:/Users/xwang222/Downloads/Amex/train.parquet',columns=['customer_ID','P_2', 'D_48', 'R_1', 'S_3', 'B_7'])
    # read targets
    target = pd.read_csv('C:/Users/xwang222/Downloads/Amex/train_labels.csv')

    all_pairs = []
    for i in range(len(high) -1):

        all_pairs.extend(list(itertools.product([high[i]], high[i+1:])))

    len(all_pairs)

    all_features = pd.DataFrame()

    for pair in all_pairs:

        aggregates = pd.DataFrame()
        aggregates['customer_ID'] = data.customer_ID

        #compute new features
        aggregates[f'{pair[0]}_t_{pair[1]}'] = data[pair[0]] * data[pair[1]]
        aggregates[f'{pair[0]}_d_{pair[1]}'] = data[pair[0]] / data[pair[1]]
        aggregates[f'{pair[0]}_p_{pair[1]}'] = data[pair[0]] + data[pair[1]]
        aggregates[f'{pair[0]}_m_{pair[1]}'] = data[pair[0]] - data[pair[1]]

        # compute aggregation
        aggregates = aggregates.groupby('customer_ID').agg(['last', 'first', 'mean', 'std', 'max', 'min'])
        aggregates.columns = ['_'.join(x) for x in aggregates.columns]
        aggregates = aggregates.fillna(0)
        aggregates.replace([np.inf, -np.inf], 0, inplace=True)

        # add target
        aggregates=aggregates.merge(target,on="customer_ID")

        # Get Information Value
        a, b = iv_woe(aggregates, 'target')

        # Select good features
        good_ones = a.loc[a.IV > 2.5].Variable.values
        all_features[good_ones] = aggregates[good_ones]

        #print('\n', 'current shape', all_features.shape, '\n')
    
    all_features['customer_ID'] = aggregates['customer_ID']
    del data
    
    return all_features

def non_linar_ts():
    high=['P_2', 'D_48', 'R_1', 'S_3', 'B_7']
        # read only categorial  features
    data = pd.read_parquet('C:/Users/xwang222/Downloads/Amex/test.parquet',columns=['customer_ID','P_2', 'D_48', 'R_1', 'S_3', 'B_7'])
    # read targets
    #target = pd.read_csv('../input/amex-default-prediction/train_labels.csv')

    all_pairs = []
    for i in range(len(high) -1):

        all_pairs.extend(list(itertools.product([high[i]], high[i+1:])))

    len(all_pairs)

    ts_features = pd.DataFrame()
    ts_features['customer_ID'] = data.customer_ID.unique()

    for pair in all_pairs:

        aggregates = pd.DataFrame()
        aggregates['customer_ID'] = data.customer_ID

        #compute new features
        aggregates[f'{pair[0]}_t_{pair[1]}'] = data[pair[0]] * data[pair[1]]
        aggregates[f'{pair[0]}_d_{pair[1]}'] = data[pair[0]] / data[pair[1]]
        aggregates[f'{pair[0]}_p_{pair[1]}'] = data[pair[0]] + data[pair[1]]
        aggregates[f'{pair[0]}_m_{pair[1]}'] = data[pair[0]] - data[pair[1]]

        # compute aggregation
        aggregates = aggregates.groupby('customer_ID').agg(['last', 'first', 'mean', 'std', 'max', 'min'])
        aggregates.columns = ['_'.join(x) for x in aggregates.columns]
        aggregates = aggregates.fillna(0)
        aggregates.replace([np.inf, -np.inf], 0, inplace=True)

        keep_features = [col for col in aggregates.columns if col in good_ones]
        print(keep_features)

        if len(keep_features)>=1:
            agg_new=aggregates[keep_features]
            ts_features=ts_features.merge(agg_new,on="customer_ID")
            
    del data
    
    return ts_features

#non_linear_tr=non_linar_tr()
#good_ones=non_linear_tr.columns.tolist()
#non_linear_ts = non_linar_ts()

def add_ftr_tr():
    df_train = pd.read_parquet('C:/Users/xwang222/Downloads/Amex/train.parquet',columns=['customer_ID','P_2','P_3','P_4','D_39','B_9','R_1','B_23','B_3','B_33','B_18','B_19','B_20','B_4','R_2','R_3','R_4','R_27','S_25','D_62','D_48','D_55','D_112'])
    df_train = df_train.groupby('customer_ID').tail(1).set_index('customer_ID')
    df_train["c_PD_239"]=df_train["D_39"]/(df_train["P_2"]*(-1)+0.0001)
    df_train["c_PB_29"]=df_train["P_2"]*(-1)/(df_train["B_9"]*(1)+0.0001)
    df_train["c_PR_21"]=df_train["P_2"]*(-1)/(df_train["R_1"]+0.0001)
    df_train["c_BBBB"]=(df_train["B_9"]+0.001)/(df_train["B_23"]+df_train["B_3"]+0.0001)
    df_train["c_BBBB1"]=(df_train["B_33"]*(-1))+(df_train["B_18"]*(-1)+df_train["S_25"]*(1)+0.0001)
    df_train["c_BBBB2"]=(df_train["B_19"]+df_train["B_20"]+df_train["B_4"]+0.0001)
    df_train["c_RRR0"]=(df_train["R_3"]+0.001)/(df_train["R_2"]+df_train["R_4"]+0.0001)
    df_train["c_RRR1"]=(df_train["D_62"]+0.001)/(df_train["D_112"]+df_train["R_27"]+0.0001)
    df_train["c_PD_348"]=df_train["D_48"]/(df_train["P_3"]+0.0001)
    df_train["c_PD_355"]=df_train["D_55"]/(df_train["P_3"]+0.0001)
    df_train["c_PD_439"]=df_train["D_39"]/(df_train["P_4"]+0.0001)
    df_train["c_PB_49"]=df_train["B_9"]/(df_train["P_4"]+0.0001)
    df_train["c_PR_41"]=df_train["R_1"]/(df_train["P_4"]+0.0001)
    df_train=df_train.drop(['P_2','P_3','P_4','D_39','B_9','R_1','B_23','B_3','B_33','B_18','B_19','B_20','B_4','R_2','R_3','R_4','R_27','S_25','D_62','D_48','D_55','D_112'], axis = 1)
        
    return df_train

def add_ftr_ts():
    df_test = pd.read_parquet('C:/Users/xwang222/Downloads/Amex/test.parquet',columns=['customer_ID','P_2','P_3','P_4','D_39','B_9','R_1','B_23','B_3','B_33','B_18','B_19'\
                                                                                                      ,'B_20','B_4','R_2','R_3','R_4','R_27','S_25','D_62','D_48','D_55','D_112'])
    df_test = df_test.groupby('customer_ID').tail(1).set_index('customer_ID')
    df_test["c_PD_239"]=df_test["D_39"]/(df_test["P_2"]*(-1)+0.0001)
    df_test["c_PB_29"]=df_test["P_2"]*(-1)/(df_test["B_9"]*(1)+0.0001)
    df_test["c_PR_21"]=df_test["P_2"]*(-1)/(df_test["R_1"]+0.0001)

    df_test["c_BBBB"]=(df_test["B_9"]+0.001)/(df_test["B_23"]+df_test["B_3"]+0.0001)
    df_test["c_BBBB1"]=(df_test["B_33"]*(-1))+(df_test["B_18"]*(-1)+df_test["S_25"]*(1)+0.0001)
    df_test["c_BBBB2"]=(df_test["B_19"]+df_test["B_20"]+df_test["B_4"]+0.0001)

    df_test["c_RRR0"]=(df_test["R_3"]+0.001)/(df_test["R_2"]+df_test["R_4"]+0.0001)
    df_test["c_RRR1"]=(df_test["D_62"]+0.001)/(df_test["D_112"]+df_test["R_27"]+0.0001)

    df_test["c_PD_348"]=df_test["D_48"]/(df_test["P_3"]+0.0001)
    df_test["c_PD_355"]=df_test["D_55"]/(df_test["P_3"]+0.0001)

    df_test["c_PD_439"]=df_test["D_39"]/(df_test["P_4"]+0.0001)
    df_test["c_PB_49"]=df_test["B_9"]/(df_test["P_4"]+0.0001)
    df_test["c_PR_41"]=df_test["R_1"]/(df_test["P_4"]+0.0001)
    df_test=df_test.drop(['P_2','P_3','P_4','D_39','B_9','R_1','B_23','B_3','B_33','B_18','B_19','B_20','B_4','R_2','R_3','R_4','R_27','S_25','D_62','D_48','D_55','D_112'], axis = 1)
    return df_test

#add_ftr_tr=add_ftr_tr()
#add_ones=add_ftr_tr.columns.tolist()
#add_ftr_ts=add_ftr_ts()

#NN_ftr_tr = pd.read_csv('C:/Users/xwang222/Downloads/Amex/NN_ftr_tr.csv')
#NN_ftr_ts = pd.read_csv('C:/Users/xwang222/Downloads/Amex/NN_ftr_ts.csv')

#CNN_FTR_TR = pd.read_csv('C:/Users/xwang222/Downloads/Amex/CNN_FTR_TR.csv')
#CNN_FTR_TS = pd.read_csv('C:/Users/xwang222/Downloads/Amex/CNN_FTR_TS.csv')

def reduce_mem_usage(df, verbose=True):
    numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
    start_mem = df.memory_usage().sum() / 1024**2
    for col in df.columns:
        col_type = df[col].dtypes
        if col_type in numerics:
            c_min = df[col].min()
            c_max = df[col].max()
            if str(col_type)[:3] == 'int':
                if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                    df[col] = df[col].astype(np.int8)
                elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                    df[col] = df[col].astype(np.int16)
                elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                    df[col] = df[col].astype(np.int32)
                elif c_min > np.iinfo(np.int64).min and c_max < np.iinfo(np.int64).max:
                    df[col] = df[col].astype(np.int64)
            else:
                if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                    df[col] = df[col].astype(np.float16)
                elif c_min > np.finfo(np.float32).min and c_max < np.finfo(np.float32).max:
                    df[col] = df[col].astype(np.float32)
                else:
                    df[col] = df[col].astype(np.float64)

    end_mem = df.memory_usage().sum() / 1024**2
    print('Memory usage after optimization is: {:.2f} MB'.format(end_mem))
    print('Decreased by {:.1f}%'.format(100 * (start_mem - end_mem) / start_mem))

    return df

col_name=['customer_ID','P_2_first', 'P_2_mean', 'P_2_std', 'P_2_min', 'P_2_max', 'P_2_last', 'D_39_first', 'D_39_mean', 'D_39_std',
 'D_39_min', 'D_39_max', 'D_39_last', 'B_1_first', 'B_1_mean', 'B_1_std', 'B_1_min', 'B_1_max', 'B_1_last', 'B_2_first', 'B_2_mean', 'B_2_std', 'B_2_min', 'B_2_max', 'B_2_last', 'R_1_first',
 'R_1_mean', 'R_1_std', 'R_1_min', 'R_1_max', 'R_1_last', 'S_3_first', 'S_3_mean', 'S_3_std', 'S_3_min', 'S_3_max', 'S_3_last', 'D_41_first', 'D_41_mean', 'D_41_std', 'D_41_min', 'D_41_max',
 'D_41_last', 'B_3_first', 'B_3_mean', 'B_3_std', 'B_3_min', 'B_3_max', 'B_3_last', 'D_42_first', 'D_42_mean', 'D_42_std', 'D_42_min', 'D_42_max', 'D_42_last', 'D_44_first', 'D_44_mean', 'D_44_std',
 'D_44_min', 'D_44_max', 'D_44_last', 'B_4_first', 'B_4_mean', 'B_4_std', 'B_4_min', 'B_4_max', 'B_4_last', 'D_45_first', 'D_45_mean', 'D_45_std', 'D_45_min', 'D_45_max', 'D_45_last', 'B_5_first',
 'B_5_mean', 'B_5_std', 'B_5_min', 'B_5_max', 'B_5_last', 'R_2_first', 'R_2_mean', 'R_2_std', 'R_2_min', 'R_2_max', 'R_2_last', 'D_46_first', 'D_46_mean', 'D_46_std', 'D_46_min', 'D_46_max',
 'D_46_last', 'D_48_first', 'D_48_mean', 'D_48_std', 'D_48_min', 'D_48_max', 'D_48_last', 'D_49_first', 'D_49_mean', 'D_49_std', 'D_49_min', 'D_49_max', 'D_49_last', 'B_6_first', 'B_6_mean', 'B_6_std',
 'B_6_min', 'B_6_max', 'B_6_last', 'B_7_first', 'B_7_mean', 'B_7_std', 'B_7_min', 'B_7_max', 'B_7_last', 'D_51_first', 'D_51_mean', 'D_51_std', 'D_51_min', 'D_51_max', 'D_51_last', 'B_9_first', 'B_9_mean',
 'B_9_std', 'B_9_min', 'B_9_max', 'B_9_last', 'R_3_first', 'R_3_mean', 'R_3_std', 'R_3_min', 'R_3_max', 'R_3_last', 'P_3_first', 'P_3_mean',
 'P_3_std', 'P_3_min', 'P_3_max', 'P_3_last', 'B_10_first', 'B_10_mean', 'B_10_std', 'B_10_min', 'B_10_max', 'B_10_last',
 'D_53_first', 'D_53_mean', 'D_53_std', 'D_53_min', 'D_53_max', 'D_53_last', 'B_11_first', 'B_11_mean', 'B_11_std', 'B_11_min', 'B_11_max', 'B_11_last', 'D_54_first', 'D_54_mean', 'D_54_std', 'D_54_min', 'D_54_max', 'D_54_last',
 'S_7_first', 'S_7_mean', 'S_7_std', 'S_7_min', 'S_7_max', 'S_7_last', 'S_8_first', 'S_8_mean', 'S_8_std', 'S_8_min',
 'S_8_max', 'S_8_last', 'S_9_first', 'S_9_mean', 'S_9_std', 'S_9_min', 'S_9_max', 'S_9_last', 'B_14_first', 'B_14_mean', 'B_14_std', 'B_14_min',
 'B_14_max', 'B_14_last', 'S_11_first', 'S_11_mean', 'S_11_std', 'S_11_min', 'S_11_max', 'S_11_last', 'D_62_first', 'D_62_mean', 'D_62_std', 'D_62_min', 'D_62_max', 'D_62_last', 'B_19_first', 'B_19_mean',
 'B_19_std', 'B_19_min', 'B_19_max', 'B_19_last', 'B_20_first', 'B_20_mean', 'B_20_std', 'B_20_min', 'B_20_max', 'B_20_last', 'D_70_first', 'D_70_mean', 'D_70_std', 'D_70_min', 'D_70_max', 'D_70_last',
 'S_15_first', 'S_15_mean', 'S_15_std', 'S_15_min', 'S_15_max', 'S_15_last', 'B_23_first', 'B_23_mean', 'B_23_std', 'B_23_min', 'B_23_max',
 'B_23_last', 'P_4_first', 'P_4_mean', 'P_4_std', 'P_4_min', 'P_4_max', 'P_4_last', 'R_9_first', 'R_9_mean', 'R_9_std', 'R_9_min', 'R_9_max', 'R_9_last', 'B_33_first', 'B_33_mean', 'B_33_std',
 'B_33_min', 'B_33_max', 'B_33_last', 'S_23_first', 'S_23_mean', 'S_23_std', 'S_23_min', 'S_23_max', 'S_23_last', 'S_25_first', 'S_25_mean', 'S_25_std', 'S_25_min', 'S_25_max', 'S_25_last', 'S_26_first',
 'S_26_mean', 'S_26_std', 'S_26_min', 'S_26_max', 'S_26_last', 'B_37_first', 'B_37_mean', 'B_37_std', 'B_37_min', 'B_37_max', 'B_37_last', 'R_27_first', 'R_27_mean', 'R_27_std', 'R_27_min', 'R_27_max',
 'R_27_last', 'B_40_first', 'B_40_mean', 'B_40_std', 'B_40_min', 'B_40_max', 'B_40_last', 'P_2_last_lag_sub', 'P_2_last_lag_div', 'D_39_last_lag_sub', 'D_39_last_lag_div', 'B_1_last_lag_sub',
 'B_1_last_lag_div', 'B_2_last_lag_sub', 'B_2_last_lag_div', 'R_1_last_lag_sub', 'R_1_last_lag_div', 'S_3_last_lag_sub', 'S_3_last_lag_div', 'D_41_last_lag_sub',
 'D_41_last_lag_div', 'B_3_last_lag_sub', 'B_3_last_lag_div', 'D_42_last_lag_sub', 'D_42_last_lag_div', 'D_44_last_lag_sub', 'D_44_last_lag_div', 'B_4_last_lag_sub',
 'B_4_last_lag_div', 'D_45_last_lag_sub', 'D_45_last_lag_div', 'B_5_last_lag_sub', 'B_5_last_lag_div', 'R_2_last_lag_sub', 'R_2_last_lag_div', 'D_46_last_lag_sub',
 'D_46_last_lag_div', 'D_48_last_lag_sub', 'D_48_last_lag_div', 'D_49_last_lag_sub', 'D_49_last_lag_div', 'B_6_last_lag_sub', 'B_6_last_lag_div', 'B_7_last_lag_sub',
 'B_7_last_lag_div', 'D_51_last_lag_sub', 'D_51_last_lag_div', 'B_9_last_lag_sub', 'B_9_last_lag_div', 'R_3_last_lag_sub', 'R_3_last_lag_div', 'P_3_last_lag_sub',
 'P_3_last_lag_div', 'B_10_last_lag_sub', 'B_10_last_lag_div', 'D_53_last_lag_sub', 'D_53_last_lag_div', 'B_11_last_lag_sub', 'B_11_last_lag_div',
 'D_54_last_lag_sub', 'D_54_last_lag_div', 'S_7_last_lag_sub', 'S_7_last_lag_div', 'S_8_last_lag_sub', 'S_8_last_lag_div', 'S_9_last_lag_sub', 'S_9_last_lag_div',
 'B_14_last_lag_sub', 'B_14_last_lag_div', 'S_11_last_lag_sub', 'S_11_last_lag_div', 'D_62_last_lag_sub', 'D_62_last_lag_div', 'B_19_last_lag_sub', 'B_19_last_lag_div',
 'B_20_last_lag_sub', 'B_20_last_lag_div', 'D_70_last_lag_sub', 'D_70_last_lag_div', 'S_15_last_lag_sub', 'S_15_last_lag_div', 'B_23_last_lag_sub', 'B_23_last_lag_div',
 'P_4_last_lag_sub', 'P_4_last_lag_div', 'R_9_last_lag_sub', 'R_9_last_lag_div', 'B_33_last_lag_sub', 'B_33_last_lag_div', 'S_23_last_lag_sub', 'S_23_last_lag_div',
 'S_25_last_lag_sub', 'S_25_last_lag_div', 'S_26_last_lag_sub', 'S_26_last_lag_div', 'B_37_last_lag_sub', 'B_37_last_lag_div', 'R_27_last_lag_sub', 'R_27_last_lag_div',
 'B_40_last_lag_sub', 'B_40_last_lag_div', 'P_2_diff1', 'D_39_diff1', 'B_1_diff1', 'B_2_diff1', 'R_1_diff1', 'S_3_diff1', 'D_41_diff1',
 'B_3_diff1', 'D_42_diff1', 'D_44_diff1', 'B_4_diff1', 'D_45_diff1', 'B_5_diff1', 'R_2_diff1', 'D_46_diff1', 'D_48_diff1', 'D_49_diff1', 'B_6_diff1', 'B_7_diff1', 'D_51_diff1', 'B_9_diff1', 'R_3_diff1', 'P_3_diff1', 'B_10_diff1',
 'D_53_diff1', 'B_11_diff1', 'D_54_diff1', 'S_7_diff1', 'S_8_diff1', 'S_9_diff1', 'B_14_diff1', 'S_11_diff1', 'D_62_diff1',
 'B_19_diff1', 'B_20_diff1', 'D_70_diff1', 'S_15_diff1', 'B_23_diff1', 'P_4_diff1', 'R_9_diff1', 'B_33_diff1', 'S_23_diff1', 'S_25_diff1', 'S_26_diff1', 'B_37_diff1', 'R_27_diff1', 'B_40_diff1', 'B_30_last', 'B_38_last', 'D_114_last', 'D_116_last', 'D_117_last', 'D_120_last', 'D_126_last', 'D_63_last', 'D_64_last', 'D_66_last', 'D_68_last','target']


def seed_everything(seed):
    random.seed(seed)
    np.random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)

def read_data():
    train = pd.read_parquet(CFG.input_dir + 'train_fe_v3.parquet',columns=col_name)
    test = pd.read_parquet(CFG.input_dir + 'test_fe_v3.parquet',columns=col_name[:-1])
    train = reduce_mem_usage(train)
    test = reduce_mem_usage(test)
    train=train.merge(non_linear_tr,how = 'inner', on = 'customer_ID').merge(add_ftr_tr,how = 'inner', on = 'customer_ID').merge(NN_ftr_tr,how = 'inner', on = 'customer_ID').merge(CNN_FTR_TR,how = 'inner', on = 'customer_ID') #merge(df_EM_tr,how = 'inner', on = 'customer_ID').
    test=test.merge(non_linear_ts,how = 'inner', on = 'customer_ID').merge(add_ftr_ts,how = 'inner', on = 'customer_ID').merge(NN_ftr_ts,how = 'inner', on = 'customer_ID').merge(CNN_FTR_TS,how = 'inner', on = 'customer_ID') #.merge(df_EM_ts,how = 'inner', on = 'customer_ID')
    #del non_linear_tr,non_linear_ts,add_ftr_tr, add_ftr_ts
    return train , test

def amex_metric(y_true, y_pred):
    labels = np.transpose(np.array([y_true, y_pred]))
    labels = labels[labels[:, 1].argsort()[::-1]]
    weights = np.where(labels[:,0]==0, 20, 1)
    cut_vals = labels[np.cumsum(weights) <= int(0.04 * np.sum(weights))]
    top_four = np.sum(cut_vals[:,0]) / np.sum(labels[:,0])
    gini = [0,0]
    for i in [1,0]:
        labels = np.transpose(np.array([y_true, y_pred]))
        labels = labels[labels[:, i].argsort()[::-1]]
        weight = np.where(labels[:,0]==0, 20, 1)
        weight_random = np.cumsum(weight / np.sum(weight))
        total_pos = np.sum(labels[:, 0] *  weight)
        cum_pos_found = np.cumsum(labels[:, 0] * weight)
        lorentz = cum_pos_found / total_pos
        gini[i] = np.sum((lorentz - weight_random) * weight)
    return 0.5 * (gini[1]/gini[0] + top_four)

def amex_metric_np(preds, target):
    indices = np.argsort(preds)[::-1]
    preds, target = preds[indices], target[indices]
    weight = 20.0 - target * 19.0
    cum_norm_weight = (weight / weight.sum()).cumsum()
    four_pct_mask = cum_norm_weight <= 0.04
    d = np.sum(target[four_pct_mask]) / np.sum(target)
    weighted_target = target * weight
    lorentz = (weighted_target / weighted_target.sum()).cumsum()
    gini = ((lorentz - cum_norm_weight) * weight).sum()
    n_pos = np.sum(target)
    n_neg = target.shape[0] - n_pos
    gini_max = 10 * n_neg * (n_pos + 20 * n_neg - 19) / (n_pos + 20 * n_neg)
    g = gini / gini_max
    return 0.5 * (g + d)

def lgb_amex_metric(y_pred, y_true):
    y_true = y_true.get_label()
    return 'amex_metric', amex_metric(y_true, y_pred), True

def train_and_evaluate(train, test):
    # Label encode categorical features
    cat_features = [
        "B_30",
        "B_38",
        "D_114",
        "D_116",
        "D_117",
        "D_120",
        "D_126",
        "D_63",
        "D_64",
        "D_66",
        "D_68"
    ]
    cat_features = [f"{cf}_last" for cf in cat_features]
    for cat_col in cat_features:
        encoder = LabelEncoder()
        train[cat_col] = encoder.fit_transform(train[cat_col])
        test[cat_col] = encoder.transform(test[cat_col])
    # Round last float features to 2 decimal place
    num_cols = list(train.dtypes[(train.dtypes == 'float32') | (train.dtypes == 'float64')].index)
    num_cols = [col for col in num_cols if 'last' in col]
    for col in num_cols:
        train[col + '_round2'] = train[col].round(2)
        test[col + '_round2'] = test[col].round(2)
    # Get the difference between last and mean
    num_cols = [col for col in train.columns if 'last' in col]
    num_cols = [col[:-5] for col in num_cols if 'round' not in col]
    for col in num_cols:
        try:
            train[f'{col}_last_mean_diff'] = train[f'{col}_last'] - train[f'{col}_mean']
            test[f'{col}_last_mean_diff'] = test[f'{col}_last'] - test[f'{col}_mean']
        except:
            pass
    # Transform float64 and float32 to float16
    num_cols = list(train.dtypes[(train.dtypes == 'float32') | (train.dtypes == 'float64')].index)
    for col in tqdm(num_cols):
        train[col] = train[col].astype(np.float16)
        test[col] = test[col].astype(np.float16)
        
    # Get feature list
    features_pre = [col for col in train.columns if col not in ['customer_ID', CFG.target]]
    #features_pre = [col for col in train.columns if ('NN_' in col) or ('P_2_' in col) or ('P_3_' in col) or ('P_4_' in col) or ('S_3_' in col) or ('S_7_' in col) or ('S_8_' in col) or ('S_9_' in col) or ('S_26_' in col) or ('S_11_' in col) or ('S_15_' in col) or ('S_23_' in col) or ('S_25_' in col) \
     #    or ('B_1_' in col) or  ('B_3_' in col) or ('B_2_' in col) or ('B_4_' in col) or ('B_5_' in col) or ('B_6_' in col) or ('B_7_' in col) or ('B_9_' in col) or ('B_10_' in col) or ('B_37_' in col) or ('B_14_' in col) or ('B_19_' in col) or ('B_20_' in col) or ('B_11_' in col) or ('B_23_' in col) or ('B_40_' in col) or ('D_39_' in col) or ('D_44_' in col) or ('D_41_' in col) or ('D_42_' in col) \
      #   or ('D_48_' in col) or ('D_45_' in col) or ('D_46_' in col) or ('D_49_' in col) or ('D_51_' in col) or ('D_53_' in col) or ('D_54_' in col) or ('D_62_' in col) or ('D_70_' in col) or ('R_2_' in col) or ('R_3_' in col) or ('R_9_' in col) or ('R_1_' in col)]+cat_features+['ever_gap_D39_x','ever_gap_D39_y']+good_ones[:-1]+add_ones
    #('B_33_' in col) or ('R_27_' in col) or 
    features_pre_set = set(features_pre)
    features = list(features_pre_set)
    
    params = {
        'objective': 'binary',
        'metric': "binary_logloss",
        'boosting': 'dart',
        'seed': CFG.seed,
        'lambda_l1': 9.281598475731823e-07,
         'lambda_l2': 1.8897002324972523e-08,
         'num_leaves': 163,
         'feature_fraction': 0.6014574068994794,
         'bagging_fraction': 0.9690065597961233,
         'bagging_freq': 6,
         'min_child_samples': 66,
         'learning_rate': 0.04,
        'n_jobs': -1,
        } #'device':'gpu'
    
    # Create a numpy array to store test predictions
    test_predictions = np.zeros(len(test))
    # Create a numpy array to store out of folds predictions
    oof_predictions = np.zeros(len(train))
    kfold = StratifiedKFold(n_splits = CFG.n_folds, shuffle = True, random_state = CFG.seed)
    
    for fold, (trn_ind, val_ind) in enumerate(kfold.split(train, train[CFG.target])):
        print(' ')
        print('-'*50)
        print(f'Training fold {fold} with {len(features)} features...')
        x_train, x_val = train[features].iloc[trn_ind], train[features].iloc[val_ind]
        y_train, y_val = train[CFG.target].iloc[trn_ind], train[CFG.target].iloc[val_ind]
        lgb_train = lgb.Dataset(x_train, y_train, categorical_feature = cat_features)
        lgb_valid = lgb.Dataset(x_val, y_val, categorical_feature = cat_features)
        model = lgb.train(
            params = params,
            train_set = lgb_train,
            num_boost_round = 6000,
            valid_sets = [lgb_train, lgb_valid],
            early_stopping_rounds = 100,
            verbose_eval = 500,
            feval = lgb_amex_metric
            )
        # Save best model
        joblib.dump(model, f'lgbm_fold{fold}_seed{CFG.seed}.pkl')
        # Predict validation
        val_pred = model.predict(x_val)
        # Add to out of folds array
        oof_predictions[val_ind] = val_pred
        # Predict the test set
        test_pred = model.predict(test[features])
        test_predictions += test_pred / CFG.n_folds
        # Compute fold metric
        score = amex_metric(y_val, val_pred)
        print(f'Our fold {fold} CV score is {score}')
        del x_train, x_val, y_train, y_val, lgb_train, lgb_valid
        gc.collect()
        
    # Compute out of folds metric
    score = amex_metric(train[CFG.target], oof_predictions)
    print(f'Our out of folds CV score is {score}')
    # Create a dataframe to store out of folds predictions
    oof_df = pd.DataFrame({'customer_ID': train['customer_ID'], 'target': train[CFG.target], 'prediction': oof_predictions})
    oof_df.to_csv(f'oof_lgbm_baseline_{CFG.n_folds}fold_seed{CFG.seed}.csv', index = False)
    # Create a dataframe to store test prediction
    test_df = pd.DataFrame({'customer_ID': test['customer_ID'], 'prediction': test_predictions})
    test_df.to_csv(f'test_lgbm_baseline_{CFG.n_folds}fold_seed{CFG.seed}.csv', index = False)

seed_everything(CFG.seed)

#df_EM_tr = Create_S_2_D_39_tr()
#df_EM_ts = Create_S_2_D_39_ts()
train = pd.read_csv('C:/Users/xwang222/Downloads/train_preproc.csv')
test = pd.read_csv('C:/Users/xwang222/Downloads/test_preproc.csv')

train = train.iloc[: , 1:]
test = test.iloc[: , 1:]

import re
train = train.rename(columns = lambda x:re.sub('[^A-Za-z0-9_]+', '', x))
test = test.rename(columns = lambda x:re.sub('[^A-Za-z0-9_]+', '', x))

#train, test= read_data()
train_and_evaluate(train, test)

df_1 = pd.read_csv(f'test_lgbm_baseline_{CFG.n_folds}fold_seed{CFG.seed}.csv')
df_1.to_csv('submission.csv', index=False)

