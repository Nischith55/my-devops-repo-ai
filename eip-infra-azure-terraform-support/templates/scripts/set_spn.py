import sys
import os
import json
import tempfile
import yaml
import base64
import pprint

from jinja2 import Template, StrictUndefined, FileSystemLoader, Environment


def main():
    # Retrieve and set azure credentails for job
    print ('Executing python script file is:' + str(sys.argv[0]))
    print ('The arguments are:'+ str(sys.argv))
    spn = str(sys.argv[1]).strip()
    print ('Getting azure credential for job execution. spn:%s' % spn)
    svc_principal = 'SP_' + spn
    print(svc_principal)
    if os.environ.get(svc_principal) is None:
        raise Exception('Service principal: {0} not found in context.'.format(spn))
    # Retrieve the SP from env
    encoded_value = os.environ[svc_principal]
    print(encoded_value)
    # Decode to get the serialized json
    base64_string = encoded_value
    base64_bytes = base64_string.encode("ascii")      
    string_bytes = base64.b64decode(base64_bytes)
    decoded_value = string_bytes.decode("ascii")

    # Hydrate the json obj
    azure_creds = json.loads(decoded_value)
   
    print ('##vso[task.setvariable variable=arm_subscription_id;isOuput=true]%s' \
        % azure_creds['subscription_id'])
    print ('##vso[task.setvariable variable=arm_client_id;isOuput=true]%s' \
        % azure_creds['client_id'])
    print ('##vso[task.setvariable variable=arm_tenant_id;isOuput=true]%s' \
        % azure_creds['tenant'])
    print ('##vso[task.setvariable variable=arm_client_secret;isOuput=true]%s' \
        % azure_creds['secret'])

    # for name, value in os.environ.items():
    #     print("{0}: {1}".format(name, value))
    
    # current_working_directory = os.getcwd()
    # print("current_working_directory",current_working_directory)

if __name__ == "__main__":
    main()