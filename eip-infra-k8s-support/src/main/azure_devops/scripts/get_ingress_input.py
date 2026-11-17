#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import requests
import sys
import json 
from openpyxl import load_workbook
from json import dumps

pat_token=sys.argv[1]
path=sys.argv[2]
#getting agentpool
f = open(path)
data = json.load(f)


#getting the workitem details
api_url = "https://dev.azure.com/PepsiCoIT/EIP-Infrastructure/_apis/wit/workitems/8880639?$expand=all&api-version=5.0"
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
ws = wb['Request Form']

all_rows = list(ws.rows)
print(f"Found {len(all_rows)} rows of data.")
final_json= {}
i=0
for cell in all_rows[5:len(all_rows)]:
    if (cell[0].value is None) or (cell[1].value is None) or (cell[2].value is None) or (cell[3].value is None) or (cell[4].value is None) or (cell[5].value is None) or (cell[6].value is None):
        print("Some input value is empty. Skipping it.")
        continue  
    final_json[i] = {}
    env=cell[1].value.lower()
    region=cell[0].value.lower()
    type=cell[2].value.lower().split("-")[1]
    # if (env == "nonprod" ) and (type =="eiap" or type=="snt"):
    #     agentpool="pep-eiap-nonprod-eus-infra-02-aks-agents"
    # elif (env == "preprod" ) and (type =="eiap" or type=="snt"):
    #     agentpool="pep-eiap-preprod-scus-infra-02-aks-agents"
    # elif (env == "prod" ) and (type =="eiap" or type=="snt"):
    #     agentpool="pep-eiap-prod-scus-infra-02-aks-agents"
    # elif (env=="nonprod" and type=="pfna"):
    #     agentpool="pep-pfna-nonprod-$(region)-hhnxt-infra-02-aks-agents"
    # elif (env=="preprod" and type=="pfna"):
    #     agentpool="pep-pfna-cit-preprod-{}-infra-02-aks-agents".format(region)
    # else:
    #     agentpool="pep-pfna-cit-prod-{}-infra-02-aks-agents".format(region)
    for k in data[env]:
        if k['cluster'] == cell[2].value.lower():
            agentpool=k['agentpool']
            break
    print(agentpool)
    final_json[i].update(
        {
            "region": cell[0].value.lower(),
            "env": cell[1].value.lower(),
            "cluster_name": cell[2].value.lower(),
            "namespace": cell[3].value.lower(),
            "service_name": cell[4].value.lower(),
            "service_port": cell[5].value,
            "application_context_path": cell[6].value.lower(),
            "env_convert": cell[1].value.upper(),
            "agentpool": agentpool
        }
    )
    i=i+1
print(final_json)
json_file=open("input.json", "w")
json_file.write(str(final_json))
json_file.close
