#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on wed
"""

from copy import deepcopy
import sys
sys.path.append('/opt/venv/python38-ansible211/lib/python3.8/site-packages')
import wheel
import pytz
import dateutil
import numpy
import six
import pandas

import json
from os import getcwd
import common_file
import csv

from itertools import zip_longest
from collections import OrderedDict
import sys
sys.path.append('/opt/venv/python38-ansible211/lib/python3.8/site-packages')
import jmespath
import json
import os

with open('constraints.json') as f:
  data = json.load(f, object_pairs_hook=OrderedDict)

search_string = "items[].{OPA_Policy_Name: metadata.name, Violations: status.violations[].{EnforcementAction: enforcementAction, Kind: kind, Message: message, Object_name: name, Namespace: namespace}}"

new = jmespath.search(search_string, data)
json_object = json.dumps(new, indent = 4, sort_keys=True)
with open("new.json", "w") as outfile:
    outfile.write(json_object)
f.close()


def cross_join(left, right):
    new_rows = [] if right else left
    for left_row in left:
        for right_row in right:
            temp_row = deepcopy(left_row)
            for key, value in right_row.items():
                temp_row[key] = value
            new_rows.append(deepcopy(temp_row))
    return new_rows


def flatten_list(data):
    for elem in data:
        if isinstance(elem, list):
            yield from flatten_list(elem)
        else:
            yield elem


def json_to_dataframe(data_in):
    def flatten_json(data, prev_heading=''):
        if isinstance(data, dict):
            rows = [{}]
            for key, value in data.items():
                rows = cross_join(rows, flatten_json(value, prev_heading + '.' + key))
        elif isinstance(data, list):
            rows = []
            for item in data:
                [rows.append(elem) for elem in flatten_list(flatten_json(item, prev_heading))]
        else:
            rows = [{prev_heading[1:]: data}]
        return rows

    return pandas.DataFrame(flatten_json(data_in))


if __name__ == '__main__':

    tools_home = getcwd()
    v_json_file = common_file.v_json_filename
    with open(tools_home+"/"+v_json_file) as fp:

        json_data = json.loads(fp.read())

    df = json_to_dataframe(json_data)
    df.drop_duplicates()
    df.pop('Violations')


    df.to_csv("CSV.csv", quoting=csv.QUOTE_ALL,index = None)

# load the resultant csv file
    result = pandas.read_csv("CSV.csv", sep='delimiter', header=None, engine='python')

