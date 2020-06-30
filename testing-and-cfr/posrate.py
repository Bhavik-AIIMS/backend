# -*- coding: utf-8 -*-
"""PosRate.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/12wc5X5MCrvvHOTyKajOrBQVz4KSehXav
"""

!pip install wget
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from subprocess import call
from scipy.stats.distributions import gamma,lognorm
import json 
import wget
import os
import os.path
from datetime import datetime
import pytz 
from collections import OrderedDict
from google.colab import drive
#os.chdir('/content/gdrive/My Drive')
drive.mount('/content/gdrive')

os.chdir('/content/gdrive/My Drive/test')

wget.download('https://api.covid19india.org/v3/data-all.json', os.getcwd()+"//test.json")

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
    return  str(dat[8:10]) + fn(str(dat[5:7]))

dataset=pd.read_csv('./population.csv')
population=pd.DataFrame()
population["State"]=dataset['State'][:37]
population["Population"]=dataset['Population'][:37]
population=population.set_index('State')

state_id = {
  "TT":"India",
  "MH":"Maharashtra",
  "TN":"Tamil Nadu",
  "DL":"Delhi",
  "GJ":"Gujarat",
  "RJ":"Rajasthan",
  "UP":"Uttar Pradesh",
  "MP":"Madhya Pradesh",
  "WB":"West Bengal",
  "KA":"Karnataka",
  "BR":"Bihar",
  "AP":"Andhra Pradesh",
  "HR":"Haryana",
  "TG":"Telangana",
  "JK":"Jammu and Kashmir",
  "OR":"Odisha",
  "PB":"Punjab",
  "AS":"Assam",
  "KL":"Kerala",
  "UT":"Uttarakhand",
  "JH":"Jharkhand",
  "CT":"Chhattisgarh",
  "TR":"Tripura",
  "HP":"Himachal Pradesh",
  "CH":"Chandigarh",
  "GA":"Goa",
  "MN":"Manipur",
  "NL":"Nagaland",
  "PY":"Puducherry",
  "LA":"Ladakh",
  "AR":"Arunachal Pradesh",
  "AN":"Andaman and Nicobar Islands",
  "ML":"Meghalaya",
  "MZ":"Mizoram",
  "DN":"Dadra and Nagar Haveli and Daman and Diu",
  "SK":"Sikkim",
}

start=datetime.now()
x=datetime.now(pytz.timezone('Asia/Kolkata')).date()
dd=pd.date_range(start="2020-01-30",end=x)
dates=[]
for i in range(len(dd)):
  dates.append((str(dd[i])[:10]))
#dates
dates1=[]
for w in range (len(dates)):
  if len(dates[w]):
    dates1.append(convert(dates[w]))
states={}
csv_dates=[]
csv_states=[]
csv_total_cases=[]
csv_cum_recovered=[]
csv_daily_recovered=[]
csv_cum_deceased=[]
csv_daily_deceased=[]
csv_positivity_rate_cumulative=[]
csv_daily_positive_cases=[]
csv_daily_positivity_rate=[]
csv_daily_positive_cases_ma=[]
csv_daily_positivity_rate_ma=[]
csv_test_per_million=[]
csv_daily_tested=[]
csv_cum_tested=[]
test=json.load(open('test.json'))
for j in state_id.keys():
  test_per_million=['']*len(dates)
  pos_cum=['']*len(dates)
  pos_rate_cum=['']*len(dates)
  daily_pos=['']*len(dates)
  daily_pos_ma=['']*len(dates)
  daily_tested=['']*len(dates)
  daily_pos_rate=['']*len(dates)
  daily_pos_rate_ma=['']*len(dates)
  tested_cum=['']*len(dates)
  tested_daily=['']*len(dates)
  deceased_cum=['']*len(dates)
  daily_deceased=['']*len(dates)
  recovered_cum=['']*len(dates)
  daily_recovered=['']*len(dates)
  for i in range(len(dates)):
    if dates[i] in test.keys():
      temp=json.load(open('test.json'))[dates[i]]
    if j in temp.keys():
      if 'total' in temp[j].keys():
        if 'confirmed' in temp[j]['total'].keys():
          pos_cum[i]=temp[j]['total']['confirmed']

        if 'tested' in temp[j]['total'].keys():
          tested_cum[i]=abs(temp[j]['total']['tested'])
          test_per_million[i]=temp[j]['total']['tested']*1000000/int(population["Population"][state_id[j]])
            
        if 'deceased' in temp[j]['total'].keys():
          deceased_cum[i]=temp[j]['total']['deceased']
        
        if 'recovered' in temp[j]['total'].keys():
          recovered_cum[i]=temp[j]['total']['recovered']
        
        if len(str(pos_cum[i])) and len(str(tested_cum[i])):
          pos_rate_cum[i]= pos_cum[i]*100/tested_cum[i]

      if 'delta' in temp[j].keys():
        if 'confirmed' in temp[j]['delta'].keys():
          daily_pos[i]=temp[j]['delta']['confirmed']

        if 'tested' in temp[j]['delta'].keys():
          daily_tested[i]=abs(temp[j]['delta']['tested'])
        
        if 'deceased' in temp[j]['delta'].keys():
          daily_deceased[i]=temp[j]['delta']['deceased']
        
        if 'recovered' in temp[j]['delta'].keys():
          daily_recovered[i]=temp[j]['delta']['recovered']
        
        if len(str(daily_pos[i])) and len(str(daily_tested[i])):
          daily_pos_rate[i]=int(daily_pos[i])*100/int(daily_tested[i])

  for w in range(7,len(daily_pos)):
    sum1=0
    sum2=0
    for s in range(7):
      if (len(str(daily_pos[w-s]))!=0 and len(str(daily_tested[w-s]))!=0):
        sum1+=int(daily_pos[w-s])
        sum2+=int(daily_tested[w-s])
    if (sum2!=0):
      daily_pos_rate_ma[w]=sum1*100/abs(sum2)
  
  for w in range(7,len(daily_pos)):
    sum1=0
    count=0
    for s in range(7):
      if (len(str(daily_pos[w-s]))!=0):
        sum1+=int(daily_pos[w-s])
        count+=1
    if count!=0:
      daily_pos_ma[w]=sum1/count

  st=state_id[j]

  for i in range(len(dates)):
    csv_dates.append(dates1[i])
    csv_states.append(st)
    csv_total_cases.append(pos_cum[i])
    csv_positivity_rate_cumulative.append(pos_rate_cum[i])
    csv_daily_positive_cases.append(daily_pos[i])
    csv_cum_recovered.append(recovered_cum[i])
    csv_daily_recovered.append(daily_recovered[i])
    csv_cum_deceased.append(deceased_cum[i])
    csv_daily_deceased.append(daily_deceased[i])
    csv_daily_positivity_rate.append(daily_pos_rate[i])
    csv_daily_positive_cases_ma.append(daily_pos_ma[i])
    csv_daily_positivity_rate_ma.append(daily_pos_rate_ma[i])
    csv_daily_tested.append(daily_tested[i])
    csv_cum_tested.append(tested_cum[i])
    csv_test_per_million.append(test_per_million[i])
  #print(st)
  states[st]={
                    'dates':dates1,
                    'cum_positive_cases':pos_cum,
                    'cum_positivity_rate':pos_rate_cum[:-1],
                    'daily_positive_cases':daily_pos[:-1],
                    'cum_recovered':recovered_cum,
                    'daily_recovered':daily_recovered[:-1],
                    'cum_deceased':deceased_cum,
                    'daily_deceased':daily_deceased[:-1],
                    'daily_positivity_rate':daily_pos_rate[:-1],
                    'daily_positive_cases_ma': daily_pos_ma[:-1],
                    'daily_positivity_rate_ma':daily_pos_rate_ma[:-1] , 
                    'daily_tests': daily_tested[:-1],
                    'cum_tests': tested_cum,
                    'test_per_million':test_per_million[:-1],    
              }
end=datetime.now()
print(end-start)

states['datetime']=str(datetime.now(pytz.timezone('Asia/Kolkata')))
with open('positivity_Rate.json', 'w') as outfile:
    json.dump(states, outfile,indent=4)

df=pd.DataFrame()
df['dates']=csv_dates
df['state']=csv_states
df['cum_positive_cases']=csv_total_cases
df['cum_positivity_rate']=csv_positivity_rate_cumulative
df['cum_recovered']=csv_cum_recovered
df['daily_recovered']:csv_daily_recovered
df['cum_deceased']=csv_cum_deceased
df['daily_deceased']:daily_deceased
df['daily_positive_cases']=csv_daily_positive_cases
df['daily_positivity_rate']=csv_daily_positivity_rate
df['daily_positive_cases_ma']=csv_daily_positive_cases_ma
df['daily_positivity_rate_ma']=    csv_daily_positivity_rate_ma
df['daily_tests']=csv_daily_tested
df['cum_tested']=csv_cum_tested
df['test_per_million']=csv_test_per_million
df.to_csv('positivity_Rate.csv',index=False)

