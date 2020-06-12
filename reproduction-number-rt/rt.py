#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!pip install wget


# In[2]:


import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from subprocess import call
from scipy.stats.distributions import gamma
import json 
import wget
import os
import os.path
import sys
#from google.colab import drive
#drive.mount('/content/gdrive')
#os.chdir('/content/gdrive/My Drive/minimal')


# In[3]:


if os.path.exists(os.getcwd()+"\\national.json"):
    os.remove(os.getcwd()+"\\national.json")
wget.download('https://api.covid19india.org/data.json', os.getcwd()+"//national.json")

if os.path.exists(os.getcwd()+"\\states.json"):
    os.remove(os.getcwd()+"\\states.json")
wget.download('https://api.covid19india.org/states_daily.json', os.getcwd()+"//states.json")
sys.path


# In[4]:


def pooled_SD(sds,means):
    return np.sqrt((np.sum(sds**2,axis=0)+np.sum(means-np.mean(means,axis=0)))/sds.shape[0])


# In[5]:


json_data = {}


# In[6]:


def fn(mon):
  if(mon == "01"):
    return " January"
  if(mon == "02"):
    return " February"
  if(mon == "03"):
    return " March"
  if(mon == "04"):
    return " April"
  if(mon == "05"):
    return " May"
  if(mon == "06"):
    return " June"
  if(mon == "07"):
    return " July"
  if(mon == "08"):
    return " August"
  if(mon == "09"):
    return " September"
  if(mon == "10"):
    return " October"
  if(mon == "11"):
    return " November"
  if(mon == "12"):
    return " December"
def convert(dat): 
    return  str(dat[3:5]) + fn(str(dat[:2]))


# ### Calculation for Rt (India - No Import Adjustment)

# In[7]:


dates = np.array([pd.to_datetime(i['date']+"2020") for i in json.load(open('national.json',))['cases_time_series']])
confirmed = np.array([int(i['dailyconfirmed'])for i in json.load(open('national.json',))['cases_time_series']])

confirmed = confirmed[dates>=pd.to_datetime("03/04/20")]
dates = dates[dates>=pd.to_datetime("03/04/20")]

real_data = confirmed

rt = []
dats = []
for n in range(10):
    print("Iteration: ",n+1,end='\r')
    dataset = np.copy(real_data)
    G = gamma(3.325+0.616*np.random.normal(),0.979+0.195*np.random.normal())
    for i in range(len(dataset)):
        send_back = np.clip(np.round(G.rvs(np.max([0,int(dataset[i])]))),0,10)
        send_back = send_back[i-send_back>=0]
        dataset[i] = 0
        for j in np.unique(np.int32(send_back)):
            dataset[i-j] += np.sum(send_back==j)
    dataset[::-1] = dataset[::-1]+np.random.negative_binomial(n=dataset[::-1]+1,p=G.cdf(np.arange(len(dataset))),size=len(dataset)) 
    df = pd.DataFrame()
    df['active'] = dataset[:-3]
    df['date'] = dates[:-3]
    df.to_csv('dataset.csv',index=False)
    call(['RScript.exe','scripts/Rt_analysis.R'])
    rt.append(pd.read_csv('rtoutput.csv'))
    dats.append(dataset[:-3])

means = np.array([x["Mean(R)"].values for x in rt])
sds = np.array([x["Std(R)"].values for x in rt])


# In[8]:


stindex = 2+5-1
unchanged=list(pd.Series(dates)[stindex:stindex+means.shape[1]].dt.strftime('%m-%d-%Y'))
changed=[]
for i in unchanged:
  changed.append(convert(i))


# In[9]:


import pandas as pd
df=pd.DataFrame()
csv_dates=[]
csv_rt_point=[]
csv_rt_sd=[]
csv_rt_l95=[]
csv_rt_u95=[]
csv_rt_l50=[]
csv_rt_u50=[]
csv_cases_mean=[]
csv_cases_sd=[]
csv_cases_dates=[]
#dates=[]
india = {
        'dates':changed,
        'rt_point':list(means.mean(axis=0)),
        'rt_sd':list(pooled_SD(sds,means)),
        'rt_l95':list(means.mean(axis=0)-1.95996*pooled_SD(sds,means)),
        'rt_u95':list(means.mean(axis=0)+1.95996*pooled_SD(sds,means)),
        'rt_l50':list(means.mean(axis=0)-0.67449*pooled_SD(sds,means)),
        'rt_u50':list(means.mean(axis=0)+0.67449*pooled_SD(sds,means)),
        'cases_mean':list(np.mean(dats,axis=0)),
        'cases_sd':list(np.std(dats,axis=0)),
        'cases_dates':list(pd.Series(dates)[:-3].dt.strftime('%m-%d-%Y'))
        }
for i in range(len(changed)):
  csv_dates.append(changed[i])
  csv_rt_point.append(list(means.mean(axis=0))[i])
  csv_rt_sd.append(list(pooled_SD(sds,means))[i])
  csv_rt_l95.append(list(means.mean(axis=0)-1.95996*pooled_SD(sds,means))[i])
  csv_rt_u95.append(list(means.mean(axis=0)+1.95996*pooled_SD(sds,means))[i])
  csv_rt_l50.append(list(means.mean(axis=0)-0.67449*pooled_SD(sds,means))[i])
  csv_rt_u50.append(list(means.mean(axis=0)+0.67449*pooled_SD(sds,means))[i])
  csv_cases_mean.append(list(np.mean(dats,axis=0))[i])
  csv_cases_sd.append(list(np.std(dats,axis=0))[i])
  csv_cases_dates.append(list(pd.Series(dates)[:-3].dt.strftime('%m-%d-%Y'))[i])
df['dates']=csv_dates
df['state']=['India']*len(csv_dates)
df['rt_point']=csv_rt_point
df['rt_sd']=csv_rt_sd
df['rt_l95']=csv_rt_l95
df['rt_u95']=csv_rt_u95
df['rt_l50']= csv_rt_l50
df['rt_u50']=csv_rt_u50
df['cases_mean']=csv_cases_mean
df['cases_sd']=csv_cases_sd
df['cases_dates']=csv_cases_dates


# In[10]:


json_data['IN'] = india


# ### State Level Data

# In[11]:


states = list(filter(lambda v:len(v)<3,list(json.load(open('states.json',))['states_daily'][0].keys())))


# In[12]:


dates = np.array([pd.to_datetime(i['date']) for i in filter(lambda v: v['status'] == 'Confirmed',json.load(open('states.json',))['states_daily'])])
data = pd.DataFrame()
for st in states:
    data[st] = np.array([i[st] for i in filter(lambda v: v['status'] == 'Confirmed',json.load(open('states.json',))['states_daily'])])


# In[13]:


data = data.replace(r'^\s*$', np.NaN, regex=True).fillna(0)
data = data.astype(np.int32)
data['date'] = dates


# In[ ]:


state_id = {
  "mh":"Maharashtra",
  "tn":"Tamil Nadu",
  "dl":"Delhi",
  "gj":"Gujarat",
  "rj":"Rajasthan",
  "up":"Uttar Pradesh",
  "mp":"Madhya Pradesh",
  "wb":"West Bengal",
  "ka":"Karnataka",
  "br":"Bihar",
  "ap":"Andhra Pradesh",
  "hr":"Haryana",
  "tg":"Telangana",
  "jk":"Jammu and Kashmir",
  "or":"Odisha",
  "pb":"Punjab",
  "as":"Assam",
  "kl":"Kerala",
  "ut":"Uttarakhand",
  "jh":"Jharkand",
  "ct":"Chhattisgarh",
  "tr":"Tripura",
  "hp":"Himachal Pradesh",
  "ch":"Chandigarh",
  "ga":"Goa",
  "mn":"Manipur",
  "nl":"Nagaland",
  "py":"Puducherry",
  "la":"Ladakh",
  "ar":"Arunachal Pradesh",
  "an":"Andaman and Nicobar Islands",
  "ml":"Meghalaya",
  "mz":"Mizoram",
  "dn":"Dadra and Nagar Haveli and Daman and Diu",
  "sk":"Sikkim",
}
for state in state_id.keys():
    csv_dates=[]
    csv_rt_point=[]
    csv_rt_sd=[]
    csv_rt_l95=[]
    csv_rt_u95=[]
    csv_rt_l50=[]
    csv_rt_u50=[]
    csv_cases_mean=[]
    csv_cases_sd=[]
    csv_cases_dates=[]
    print("\n",state)
    boots = 10
    real_data = data[state].values
    active = pd.DataFrame()
    active['active'] = real_data
    active.to_csv('dataset.csv',index=False)
    rt = []
    dats = []
    for n in range(boots):
        print("Iteration: ",n+1,end='\r')
        G = gamma(3.325+0.616*np.random.normal(),0.979+0.195*np.random.normal())
        dataset = np.copy(real_data)
        for i in range(len(dataset)):
            send_back = np.clip(np.round(G.rvs(np.max([0,int(dataset[i])]))),0,10)
            send_back = send_back[i-send_back>=0]
            dataset[i] = 0
            for j in np.unique(np.int32(send_back)):
                dataset[i-j] += np.sum(send_back==j)
        dataset[::-1] = dataset[::-1]+np.random.negative_binomial(n=dataset[::-1]+1,p=G.cdf(np.arange(len(dataset))),size=len(dataset)) 
        active = pd.DataFrame()
        active['active'] = dataset[:-3]
        active['date'] = dates[:-3]
        dats.append(dataset[:-3])
        active.to_csv('dataset.csv',index=False)
        call(['RScript.exe','scripts/Rt_analysis.R'])
        rt.append(pd.read_csv('rtoutput.csv'))

    means = np.array([x["Mean(R)"].values for x in rt])
    sds = np.array([x["Std(R)"].values for x in rt])
    dat_means = np.mean(dats,axis=0)
    dat_sds = np.std(dats,axis=0)
    unchanged=list(pd.Series(dates)[stindex:stindex+means.shape[1]].dt.strftime('%m-%d-%Y'))
    changed=[]
    unchanged=list(pd.Series(dates)[stindex:stindex+means.shape[1]].dt.strftime('%m-%d-%Y'))
    for i in unchanged:
      changed.append(convert(i))
    stindex = 2+5-1
    temp = {
            'dates':changed,
            'rt_point':list(means.mean(axis=0)),
            'rt_sd':list(pooled_SD(sds,means)),
            'rt_l95':list(means.mean(axis=0)-1.95996*pooled_SD(sds,means)),
            'rt_u95':list(means.mean(axis=0)+1.95996*pooled_SD(sds,means)),
            'rt_l50':list(means.mean(axis=0)-0.67449*pooled_SD(sds,means)),
            'rt_u50':list(means.mean(axis=0)+0.67449*pooled_SD(sds,means)),
            'cases_mean':list(np.mean(dats,axis=0)),
            'cases_sd':list(np.std(dats,axis=0)),
            'cases_dates':list(pd.Series(dates)[:-3].dt.strftime('%m-%d-%Y'))
            }
    state_df=pd.DataFrame()
    for i in range(len(changed)):
      csv_dates.append(changed[i])
      csv_rt_point.append(list(means.mean(axis=0))[i])
      csv_rt_sd.append(list(pooled_SD(sds,means))[i])
      csv_rt_l95.append(list(means.mean(axis=0)-1.95996*pooled_SD(sds,means))[i])
      csv_rt_u95.append(list(means.mean(axis=0)+1.95996*pooled_SD(sds,means))[i])
      csv_rt_l50.append(list(means.mean(axis=0)-0.67449*pooled_SD(sds,means))[i])
      csv_rt_u50.append(list(means.mean(axis=0)+0.67449*pooled_SD(sds,means))[i])
      csv_cases_mean.append(list(np.mean(dats,axis=0))[i])
      csv_cases_sd.append(list(np.std(dats,axis=0))[i])
      csv_cases_dates.append(list(pd.Series(dates)[:-3].dt.strftime('%m-%d-%Y'))[i])
    state_df['dates']=csv_dates
    state_df['state']=[state]*len(csv_dates)
    state_df['rt_point']=csv_rt_point
    state_df['rt_sd']=csv_rt_sd
    state_df['rt_l95']=csv_rt_l95
    state_df['rt_u95']=csv_rt_u95
    state_df['rt_l50']= csv_rt_l50
    state_df['rt_u50']=csv_rt_u50
    state_df['cases_mean']=csv_cases_mean
    state_df['cases_sd']=csv_cases_sd
    state_df['cases_dates']=csv_cases_dates
    df=pd.concat([df,state_df])
    json_data[state] = temp


# In[ ]:


df.to_csv('rt.csv',index=False)


# In[ ]:


json_data_indented =  json.dump(json_data, indent = 4)
with open("rt.json", "w") as outfile: 
    outfile.write(json_data_indented)


# In[ ]:




