#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from json import dumps

script_dir=sys.argv[2]
env=sys.argv[1]
others='test'
f = open(script_dir)
# returns JSON object as 
# a dictionary
data = json.load(f)
final_json = {}
j=0
for i in data[env]:
    final_json[j] = {}
    final_json[j].update(i)
    j=j+1
print(final_json)
name='data_json'
print(f'##vso[task.setvariable variable={name};isOutput=true]{final_json}')
# Closing file
f.close()