#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
import sys
import json 
from openpyxl import load_workbook
from json import dumps
import re 
import yaml 

pat_token=sys.argv[1]
cluster_name=sys.argv[2]
env=sys.argv[3]
type=sys.argv[4]
region=sys.argv[5]
print(cluster_name)
#getting the workitem details
api_url = "https://dev.azure.com/PepsiCoIT/EIP-Infrastructure/_apis/wit/workitems/10121880?$expand=all&api-version=5.0"
response = requests.get(api_url, headers={'Content-Type': 'application/json-patch+json'},auth=('', pat_token))
response.raise_for_status()
# print(response.json())
if response.status_code != 204:
    print(response.json())

json_str = json.dumps(response.json())
resp = json.loads(json_str)
# print(resp)
attachment_id = resp['relations'][0]['attributes']['id']
fileName = resp['relations'][0]['attributes']['name']
attachment_url = resp['relations'][0]['url']
print(attachment_id)

#downloading the excel from work item
attach_url = "{}?fileName={}&download=true&api-version=7.0".format(attachment_url, fileName)
response = requests.get(attach_url, headers={'Content-Type': 'application/json-patch+json'},auth=('', pat_token))
response.raise_for_status()
open("input.xlsx", "wb").write(response.content)

#reading excel data
wb = load_workbook('input.xlsx')
#ws = wb['APP CI - Namespace Mapping']
ws = wb['NS-TAGGING']
all_rows = list(ws.rows)
print(f"Found {len(all_rows)} rows of data.")
final_json = {}
final_json["data"]=[]
i=0
for cell in all_rows[1:len(all_rows)]:
    if (cell[0].value is None) or (cell[1].value is None) or (cell[2].value is None) or (cell[3].value is None) or (cell[4].value is None):
        print("Some input value is empty. Skipping it.")
        continue 
    cluster=cell[0].value.lower().strip()
    if ( cluster == cluster_name ):
        final_json["data"].append(
        {
            "namespace": cell[1].value.lower().strip(),
            "pep_cmdb_bus_app_id": cell[3].value.lower().strip(),
            "pep_cmdb_app_service_id": cell[2].value.lower().strip(),
            "pep_environment": cell[4].value.strip()
        }
        )

# yaml_data=yaml.dump(final_json)
print("hello")
print(final_json)
json_data=json.dumps(final_json)
json_file=open("input.json", "w")
json_file.write(str(json_data))
json_file.close

# with open("input.json", 'w') as json_file:
#     json.dump(final_json, json_file, indent=2, separators=(',',': '))