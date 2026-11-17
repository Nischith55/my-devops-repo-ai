#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import base64


def main():
    print("Python version")
    print (sys.version)

    print ('Executing python script file is:' + str(sys.argv[0]))
    print ('The arguments are:' + str(sys.argv))

    # Env vars to retrieve
    env_var_names = sys.argv[1]

    # list of vars in group vars
    env_vars = env_var_names.split(':')

    try:
        # Loop throgh the list of variables
        for sp_name in env_vars:
            print ('Retrieving value for:' + sp_name)
            value = os.environ[sp_name]
            sp = 'SP_' + sp_name
            print ('value from env is : ' + value )
            # Decode the string
            decoded_value = base64.b64decode(value)
            decoded_value = str(decoded_value, 'utf-8')

            # Split the string with double spaces first 
            # and then extract the kv pair to a dictionary object
            dict_creds = dict(x.replace('=', ' ', 1).split(' ') for x in
                            decoded_value.split('  '))

            # Serialize the dictionary to a json object
            string_bytes = json.dumps(dict_creds).encode("ascii")
            # Encode the string
            base64_bytes = base64.b64encode(string_bytes)
            base64_string = base64_bytes.decode("ascii")
            serlialized_creds = base64_string

            # Set the encoded sting as variable.
            # This variable will be retrieved as needed in the workflow parsing script
            print('##vso[task.setvariable variable={0};]{1}'.format(sp, serlialized_creds))

    except Exception as ex:
        print("Error occurred while retrieving/decrytping azure kv secrets")
        print(ex)
        raise ex

if __name__ == "__main__":
    main()
