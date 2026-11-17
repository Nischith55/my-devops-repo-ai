#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import json
import tempfile
import yaml
import base64
import pprint

from jinja2 import Template, StrictUndefined, FileSystemLoader, Environment

#################################################################################

def split_workflow_step(workflow_step):
    workflow_step = workflow_step.strip()
    if '=>' in workflow_step:
        dict_step = workflow_step.split("=>")
        step_name = dict_step[0].strip()
        job_name = dict_step[1].strip()
    else:
        step_name = ''
        job_name = workflow_step
    print ('Step:{0} Job:{1}'.format(step_name, job_name))
    return (step_name, job_name)


##################################################################################

def get_jinja_vars_from_env_vars(step):

    # Get variables from env vars
    common_vars = os.environ['DICT_COMMON_PARAMS']
    job_vars = os.environ['DICT_JOB_PARAMS']

    # Convert to dictionary of key value pair
    dict_common_vars = json.loads(common_vars)
    dict_job_vars = json.loads(job_vars)

    # Merge step specific vars and common vars into one dictionary
    dict_merged = dict_common_vars
    for (k, v) in dict_job_vars.items():
        key = k.strip()
        value = v.strip()

        # only pick the step specific vars
        if key.startswith(step):
            var_key = key.split(":")[-1].strip()
            dict_merged[var_key] = value

    return dict_merged


#################################################################################

def render_jinja(vars, template_file):

    # template_file = ''

    rendered_value = ''
    try:
        # Load the template from filesystem
        templateLoader = FileSystemLoader(tempfile.gettempdir())
        templateEnv = Environment(loader=templateLoader, undefined=StrictUndefined)
        template = templateEnv.get_template(template_file)
       
        # Get the data for template rendering
        data = eval(json.dumps(vars))
        print('Data for rendering J2')
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(vars)

        # Render the template
        rendered_value = template.render(data)
        print ('Rendered jinja template  sucessfully')
    except Exception as ex:
        print('Unexpected error in render_jinja()')
        print(ex)
        raise ex
    return rendered_value


#################################################################################

def filter_workflow_step(workflow_file, task):
    print ('Filtering workflow file for task {0}'.format(task))
    try:
        with open(workflow_file, 'r') as stream:
            text = stream.read()
        data = yaml.safe_load(text)
    except (yaml.YAMLError) as y:
        print('Invalid yaml file')
        print(y)
        raise y
    except Exception as ex:
        print('Unexpected error in filter_workflow_step()')
        print(ex)
        raise ex

    validate_key_exists(data, 'workflow')
    validate_key_exists(data['workflow'], 'jobs')

    jobs = data['workflow']['jobs']

    # Remove all the jobs from workflow except the task we are interested in
    # This is needed for proper jinja substitution
    for a in (data['workflow']['jobs'])[:]:
        if a['key'].strip() != task:
            data['workflow']['jobs'].remove(a)

    print("Filtered template:")
    pp = pprint.PrettyPrinter(indent=4)
    pp.pprint(data)

    # Save the filtered template in filesystem
    # Woorking with the yaml object leads to some formatting issue in J2 templating
    temp_dir = tempfile.gettempdir()
    template_file_name = "j2_template"
    template_file = os.path.join(temp_dir, template_file_name)

    # delete the file if exists
    if os.path.exists(template_file):
        os.remove(template_file)

    with open(template_file, 'w') as tmplt:
      documents = yaml.dump(data, tmplt)

    return template_file_name


# ######################################set_azure_creds#########################################

def set_azure_creds(spn):

    # Retrieve and set azure credentails for job

    print ('Getting azure credential for job execution. spn:%s' % spn)
    svc_principal = 'SP_' + spn

    if os.environ.get(svc_principal) is None:
        raise Exception('Service principal: {0} not found in context.'.format(spn))

    # Retrieve the SP from env
    encoded_value = os.environ[svc_principal]

    # Decode to get the serialized json
    base64_string = encoded_value
    base64_bytes = base64_string.encode("ascii")       
    string_bytes = base64.b64decode(base64_bytes) 
    decoded_value = string_bytes.decode("ascii") 

    # Hydrate the json obj
    azure_creds = json.loads(decoded_value)
    print ('##vso[task.setvariable variable=AZURE_SUBSCRIPTION_ID;]%s' \
        % azure_creds['subscription_id'])
    print ('##vso[task.setvariable variable=AZURE_CLIENT_ID;]%s' \
        % azure_creds['client_id'])
    print ('##vso[task.setvariable variable=AZURE_TENANT;]%s' \
        % azure_creds['tenant'])
    print ('##vso[task.setvariable variable=AZURE_SECRET;]%s' \
        % azure_creds['secret'])


# ######################################validate keys#########################################

def validate_key_exists(dict, key):
    if key not in dict:
        raise Exception('Error in parsing workflow file. Key:{0} not found'.format(key))


# ######################################validate keys#########################################

def validate_workflow_file(workflow, task):
    try:
        data = yaml.safe_load(workflow)
    except (yaml.YAMLError) as y:
        print('Invalid workflow yaml file')
        print(y)
        raise y
    except Exception as ex:
        print('Unexpected error in validate_workflow_file()')
        print(ex)
        raise ex

    task_found = 0
    job_exists = False

    validate_key_exists(data['workflow'], 'service_principal')

    jobs = data['workflow']['jobs']
    service_principal = data['workflow']['service_principal']

    # Loop the list of jobs
    for item in jobs:

        # Validate yaml
        validate_key_exists(item, 'id')
        validate_key_exists(item, 'key')

        id = int(item['id'])
        key = str(item['key']).strip()

        if key != task:
            continue
        elif key == task:
            print ('Validating playbook params for job key=%s' % key)

            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(item)

            # global job_exists
            job_exists = True

            # global task_found
            task_found = task_found + 1

            if task_found > 1:
                raise Exception('Key:{0} occurs mutiple times in workflow file.'.format(key))

            # Validate yaml
            # validate_key_exists(item, 'name')
            validate_key_exists(item, 'playbook')
            validate_key_exists(item, 'inventory_env')
            validate_key_exists(item, 'inventory_default')
            validate_key_exists(item, 'extra_vars')

            # job_name = item['name']
            playbook = item['playbook']
            inventory_env = item['inventory_env']
            inventory_def = '$(system.defaultWorkingDirectory)/' \
                + item['inventory_default']
            extra_vars = item['extra_vars']

            # Build ansible task args
            print ('Validating extra_vars.')
            str_args = ', '.join('{0}'.format(i) for i in extra_vars)
            str_args = '{' + str_args.replace('{', '').replace('}', '') \
                + '}'
            str_args = '-i {0} -e "{1}"'.format(inventory_def, str_args)

            # Check if job level spn exists
            if 'service_principal' in item:
                service_principal = item['service_principal']

            set_azure_creds(service_principal)
            print ('Validation successfull.')

    if not job_exists:
        raise Exception('Job:{0} not found in workflow file.'.format(task))
