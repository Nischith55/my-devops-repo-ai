#!/usr/bin/python3
import os
import json
import ast
import subprocess
import yaml
import sys
import time
from yaml.loader import SafeLoader
from collections import OrderedDict
def py_dict():
    with open(sys.argv[1], 'r') as f:
        py = json.load(f)
    return py
def get_pdb_labels(js):
    subprocess.check_output(["kubectl" " get" " pdb" " -A" " -o" " json" " |" " jq -r '[.items[] | select(.spec.minAvailable) |{name: .metadata.name, minAvailable: .spec.minAvailable}]'"], shell=True)
    for j in range(len(js)):
        flag = False
        for key,value in js[j]['label'].items():
            pdb_namespace_name=js[j]['namespace']
            pdb_minavailable_parameter=js[j]['minAvailable']
            sys.stdout.flush()
            process = subprocess.check_output(["kubectl" " -n" " %s" " get" " deploy" " -l" " %s=%s" " -o" " json" " |" " jq -r '.items[] | select(.spec.replicas == %s) | {name: .metadata.name, replicas: .spec.replicas}'"%(pdb_namespace_name, key, value, pdb_minavailable_parameter)], shell=True)
            process1 = process.decode('utf-8')
            if process1 == "":
                flag = True
                break
        if flag == False:
            print("pdb name with condition .minAvailable == .spec.replicas is",js[j]['name'])

if __name__== "__main__":
    js=py_dict()
    get_pdb_labels(js)