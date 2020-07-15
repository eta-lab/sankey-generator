# -----------------------------------------------
# Skyspark API Pull to InfluxDB API Push
# Generic script for processing UBC EWS data
# Author: Dr. Adam Rysanek
# Date: 14.11.2018
# -----------------------------------------------

from functools import singledispatch
from influxdb import InfluxDBClient
from datetime import datetime
import pytz
import json
import pyhaystack
import hszinc
hszinc.MODE_ZINC
import logging
import sys
import traceback
from datetime import timedelta

# JSON Clean-up Definitions - used for removing Null values and making JSON parsing a bit easier
@singledispatch
def remove_null_bool(ob):
    return ob

@remove_null_bool.register(list)
def _process_list(ob):
    return [remove_null_bool(v) for v in ob if v is not None]

@remove_null_bool.register(dict)
def _process_list(ob):
    return {k: remove_null_bool(v) for k, v in ob.items() if v is not None}

# Establish time zones
utc = pytz.utc
pacific = pytz.timezone('Canada/Pacific')

# Connect to SkySpark using PyHaystack (with bugs corrected on local machine)
session = pyhaystack.connect('skyspark',
                            uri='https://skyspark.energy.ubc.ca',
                            username='cdemers',
                            password='UW00ut43$',
                            project = 'ubcv',
                            pint=True,
                            grid_format=hszinc.MODE_JSON,
                            http_args={'debug':False},
                             )

# Pull data from generic API call made avaialble by UBC EWS team
#data_pull = session.get_eval("apiDataTransfer()")

dateRange="2019-07-15"
d=datetime(year=2019,month=7,day=14)
while d.strftime('%Y-%m-%d')!="2019-08-15":
    d = d + timedelta(days=1)
    print(d.strftime('%Y-%m-%d'))

    data_pull = session.get_eval("readAll(equipRef->meter).hisRead("+d.strftime('%Y-%m-%d')+").table")
    data_pull.wait()
    data_json=remove_null_bool(json.loads(hszinc.dump(data_pull.result, mode=hszinc.MODE_JSON)))

    # Error logger
    err = open('errorLogger.txt','w+')

    # Parse and process JSON output from SkySpark API call
    # This script extracts all discernable values received from the API call and uses the JSON
    # metadata to assign tags. A new JSON item is created 'json_post_to_influx' which stores
    # all processed datapoints prior to pushing them to InfluxDb

    i=0
    nItems = len(data_json['rows'])
    json_post_to_influx = []

    for item in data_json['rows']:
        for k,v in item.items():
            if k!='ts':
                #print(k + "," + str(i))
                index=int(k[1:])
                timestamp_SkySpark=data_json['rows'][i]['ts'][2:].rsplit('-',1)[0]
                timestamp_datetime = datetime.strptime(timestamp_SkySpark, "%Y-%m-%dT%H:%M:%S")
                timestamp_datetime_TZ = pacific.localize(timestamp_datetime)
                timestamp_utc = timestamp_datetime_TZ.astimezone(utc)
                timestamp=timestamp_utc.strftime('%Y-%m-%dT%H:%M:%S')+"Z"

                try:
                    etrack=1
                    siteRef=data_json['cols'][index+1]['siteRef'].split(' ',1)[1]
                    etrack=2
                    groupRef=data_json['cols'][index+1]['groupRef'].split(' ',1)[1]
                    etrack=3
                    equipRef=data_json['cols'][index+1]['equipRef'].split(siteRef+" ",1)[1]
                    etrack=4
                    try:
                        typeRef=data_json['cols'][index+1]['id'].split(equipRef+" ",1)[1]
                    except:
                        id='omit'
                    etrack=5
                    try:
                        unit = data_json['cols'][index+1]['unit'][2:]
                    except KeyError:
                        unit = 'omit'
                    etrack=6

                    if type(v)==bool:
                        if v==True:
                            value=1.0
                        else:
                            value=0.0
                    try:
                        value=float(v[2:].split(' ',1)[0])
                    except:
                        if v=='OCCUPIED':
                            value=1.0
                        else:
                            value=0.0

                    json_post_information = {
                        "measurement": "UBC_EWS",
                        "tags": {
                            "siteRef": siteRef,
                            "groupRef": groupRef,
                            "equipRef": equipRef,
                            "typeRef": typeRef,
                            "unit": unit
                        },
                        "time": timestamp,
                        "fields": {
                            "value": value
                        }
                    }

                    json_post_to_influx.append(json_post_information)

                except:
                    #err.write(json.dumps(data_json['cols'][index+1]) + '\n')

                    # err.write('Error type ' + str(etrack) +'\n')
                    # if etrack==1:
                    #    err.write('Error description: Site reference does not have a differentiable name (i.e., it is not a typical string)\n')
                    # if etrack==2:
                    #    err.write('Error description: Group reference does not have a differentiable name (i.e., it is not a typical string)\n')
                    # if etrack==3:
                    #    err.write('Error description: Equipment reference cannot be parsed from site reference name (i.e., siteRef should be a sub string within equipRef)\n')
                    # if etrack==4:
                    #    err.write('Error description: ID reference does not have a differentiable name (i.e., it is not a typical string)\n')
                    # err.write('siteRef: ' + json.dumps(data_json['cols'][index+1]['siteRef']) +'\n')
                    # err.write('groupRef: ' + json.dumps(data_json['cols'][index+1]['groupRef']) +'\n')
                    # err.write('equipRef: ' + json.dumps(data_json['cols'][index+1]['equipRef']) +'\n')
                    # err.write('id: ' + json.dumps(data_json['cols'][index+1]['id']) +'\n')
                    # if etrack==5:
                    #    err.write(json.dumps(data_json['cols'][index+1]['unit']) +'\n')
                    # if etrack==6:
                    #    err.write("Unexpected error: " + sys.exc_info()[0] + '\n')
                    # err.write('--------------------------------------- \n')
                    # #print("Unexpected error:", sys.exc_info()[0])
                    continue

        i+=1

    # Connect to InfluxDB Server and post data
    client = InfluxDBClient('206.12.88.106',8086, 'root', 'root', 'sankey_generator_DB')
    client.write_points(json_post_to_influx)

# Write JSON to file
# f = open('testdump.txt','w+')
# f.write(json.dumps(data_json))
# f.close()
# f = open('testdump2.txt','w+')
# f.write(json.dumps(json_post_to_influx))
# f.close()
err.close()
