

# <<<<<<<<<<<<<<<------------------------- with max_surge ---------------------------------->>>>>>>>>>>>>>>>>>>>>>>>>>>

import sys
loc = str(sys)
from hcl2 import loads
import json
from hcl2 import loads
import json

version_upgrade_type = str(sys.argv[2])    # control_plane_upgrade system_pool_upgrade , user_pool_upgrade
print(version_upgrade_type)

def convert_dict_to_format(d, indent=0):
    result = ""
    for key, value in d.items():
        if isinstance(value, dict):
            result += " " * indent + f"{key} = " + "{\n"
            result += convert_dict_to_format(value, indent + 2)
            result += " " * indent + "}\n"
        elif isinstance(value, list):
            if key == "max_surge":
                if not value:
                    result += " " * indent + f"{key} = [] #set this to [] if not using this property while AKS creation\n"
                else:
                    result += " " * indent + f"{key} = {value} #set this to [] if not using this property while AKS creation\n"

            elif key == "linux_profile_enabled":
                if not value:
                    result += " " * indent + f"{key} = [] #set this as [\"true\"] to enable ssh connections to node pools; user name and\n #password will be picked up from pipeline variables \n    \n#windows_profile\n"
                else:
                    result += " " * indent + f"{key} = {value} #set this as [\"true\"] to enable ssh connections to node pools; user name and\n #password will be picked up from pipeline variables\n   \n #windows_profile\n"

            elif key == "windows_profile_enabled":
                if not value:
                    result += " " * indent + f"{key} = [] #if using windows profile or windows aks cluster, set this variable as [\"true\"];\n # user name and #password will be picked up from pipeline variables \n"
                else:
                    result += " " * indent + f"{key} = {value} #if using windows profile or windows aks cluster, set this variable as [\"true\"];\n # #user name and #password will be picked up from pipeline variables \n"

            elif key == "node_taints":
                if not value:
                    result += " " * indent + f"{key} = [] #this is always blank for default node pool\n"
                else:
                    result += " " * indent + f"{key} = {value} #this is always blank for default node pool\n"

            elif key == "node_zones":
                if not value:
                    result += " " * indent + f"{key} = [] \n"
                else:
                    result += " " * indent + f"{key} = {value} \n"

            elif key == "storage_profile_enabled":
                if not value:
                    result += " " * indent + f"{key} = [] #set this as [\"true\"] to use this property\n"
                else:
                    result += " " * indent + f"{key} = {value} #set this as [\"true\"] to use this property\n"


            elif key == "workload_autoscaler_profile":
                if not value:
                    result += " " * indent + f"{key} = []  #set this as [\"true\"] to use this property \n"
                else:
                    result += " " * indent + f"{key} = {value} #set this as [\"true\"] to use this property\n"


            elif key == "key_vault_secrets_provider_enabled":
                if not value:
                    result += " " * indent + f"{key} = []  #set this as [\"true\"] to use this property\n   #oidc issuer\n"
                else:
                    result += " " * indent + f"{key} = {value} #set this as [\"true\"] to use this property\n   #oidc issuer\n"

            elif key == "oms_agent_enabled":
                if not value:
                    result += " " * indent + f"{key} = []  #set this as [\"true\"] to use this property\n"
                else:
                    result += " " * indent + f"{key} = {value} #set this as [\"true\"] to use this property\n"

            else:
                result += " " * indent + f"{key} = {value}\n"
        
        elif isinstance(value, bool):
            if key == "ad_private_cluster_public_fqdn_enabled":
                result += " " * indent + f"{key} = {str(value).lower()}   \n\n  #auto_scaler_profile  \n"
            elif key == "as_skip_nodes_with_system_pods":
                result += " " * indent + f"{key} = {str(value).lower()}    \n\n #linux_profile \n"
            elif key == "only_critical_addons_enabled":
                result += " " * indent + f"{key} = {str(value).lower()}     #changing this property to true will taint the default node pool \n  #with \"CriticalAddonsOnly=true:NoSchedule\" taint\n"
            elif key == "blobCsiDriver":
                result += " " * indent + f"{key} = {str(value).lower()}    #default value\n"
            elif key == "diskCsiDriver":
                result += " " * indent + f"{key} = {str(value).lower()}    #default value\n"
            elif key == "fileCsiDriver":
                result += " " * indent + f"{key} = {str(value).lower()}    #default value\n"
            elif key == "snapshotController":
                result += " " * indent + f"{key} = {str(value).lower()}    #default value\n\n"
            elif key == "oidc_issuer_enabled":
                result += " " * indent + f"{key} = {str(value).lower()}    \n#oms agent\n"
            elif key == "secret_rotation_enabled":
                result += "#key vault secret\n"
                result += " " * indent + f"{key} = {str(value).lower()}\n"

            else:
                result += " " * indent + f"{key} = {str(value).lower()}\n"
        elif isinstance(value, (int, float)):
            if key == "node_count":
                result += " " * indent + f"{key} = {value}  \n"  #use this to handle int and float comment
            else:
                result += " " * indent + f"{key} = {value}\n"
        elif value is None:
            if key == "secret_rotation_enabled":
                result += "#key vault secret\n"
                result += " " * indent + f"{key} = null\n"
            else:
                result += " " * indent + f"{key} = null\n"


        elif key == "os_sku":
            result += " " * indent + f"{key} = '{value}' #set to 'Windows2019' or 'Windows2022' to use windows\n"
        elif key == "sku_tier":
            result += " " * indent + f"{key} = '{value}' \n\n#azure_active_directory_role_based_access_control\n"
        elif key == "wp_license":
            result += " " * indent + f"{key} = '{value}' #only possible value is \"Windows_Server\"\n\n #network_profile\n"
        elif key == "np_service_cidr":
            result += " " * indent + f"{key} = '{value}' \n\n#default_node_pool\n"
        elif key == "temporary_name_for_rotation":
            result += " " * indent + f"{key} = '{value}' #DO NOT CHANGE THIS PROPERTY\n\n#storage_profile_enabled\n"
        elif '/' in key:
            result += " " * indent + f"\"{key}\" = \"{value}\"\n"
        else:
            result += " " * indent + f"{key} = \"{value}\"\n"
    return result


if version_upgrade_type == "control_plane_upgrade":
    with open(str(sys.argv[7]), 'r') as f:
        tfvars_content = f.read()
    # Parse the .tfvars content using hcl2
    parsed_vars = loads(tfvars_content)

    versions = str(sys.argv[4])
    versions = versions.replace(" ", "")
    versions = versions.split(",")
    while("" in versions):
        versions.remove("")
    versions = versions[0] # it will take 1st valid version 
                               # put argv of resource-name
    parsed_vars["aks_clusters"][str(sys.argv[5])]["orchestrator_version"] = versions # (put argv of versions parameter)

    data = parsed_vars

    formatted_data = convert_dict_to_format(data)
    modified_content = formatted_data.replace("'", '"')

    output_file_path = str(sys.argv[7])

    with open(output_file_path, "w") as output_file:
        output_file.write(modified_content)

    with open(str(sys.argv[6]), 'r') as fs:
        tfvars_contents = fs.read()
    # Parse the .tfvars content using hcl2
    parsed_varss = loads(tfvars_contents)

    kubernetes_versions = str(sys.argv[4])
    kubernetes_versions = kubernetes_versions.replace(" ", "")
    kubernetes_versions = kubernetes_versions.split(",")
    while("" in kubernetes_versions):
        kubernetes_versions.remove("")
    kubernetes_versions = kubernetes_versions[0] # it will take 1st valid version 

    parsed_varss["kubernetes_version"] = kubernetes_versions      #(put argv of newly created kubernetes_version parameter)
    datas = parsed_varss

    formatted_datas = convert_dict_to_format(datas)
    modified_contents = formatted_datas.replace("'", '"')

    output_file_paths = str(sys.argv[6])

    with open(output_file_paths, "w") as output_files:
        output_files.write(modified_contents)

else:
    with open(str(sys.argv[1]), 'r') as f:
        tfvars_content = f.read()
    # Parse the .tfvars content using hcl2
    parsed_vars = loads(tfvars_content)

    if version_upgrade_type == "system_pool_upgrade":
        mode_type = "System"
    else:
        mode_type = "User"

    list_of_nodepools = []
    versions = []
    list_of_nodepools = str(sys.argv[3])
    versions = str(sys.argv[4])

    if version_upgrade_type == "system_pool_upgrade" and list_of_nodepools != "all":
        list_of_nodepools = "all"

    if list_of_nodepools == "all":
        versions = versions.replace(" ", "")
        versions = versions.split(",")
        while ("" in versions):
            versions.remove("")
        versions = versions[0]  # it will take 1st valid versions
        list_of_np = [np_name for np_name, np_config in parsed_vars["node_pools"].items() if np_config["mode"] == mode_type]

        sum_of_nodepools = len(list_of_np)
        for i in range(0, sum_of_nodepools):
            if (parsed_vars["node_pools"][list_of_np[i]]["mode"]) == mode_type:
                parsed_vars["node_pools"][list_of_np[i]]["orchestrator_version"] = versions

    else : 
        if list_of_nodepools[0] != "all":
            list_of_nodepools = list_of_nodepools.replace(" ", "")
            list_of_nodepools = list_of_nodepools.split(",")
            while ("" in list_of_nodepools):
                list_of_nodepools.remove("")
            versions = versions.replace(" ", "")
            versions = versions.split(",")
            while ("" in versions):
                versions.remove("")

            if len(versions) != len(list_of_nodepools):
                versions = versions[0]
                sum_of_nodepools = len(list_of_nodepools)
                for i in range(0, sum_of_nodepools):
                    if (parsed_vars["node_pools"][list_of_nodepools[i]]["mode"]) == mode_type:
                        parsed_vars["node_pools"][list_of_nodepools[i]]["orchestrator_version"] = versions     
            else:          
                sum_of_nodepools = len(list_of_nodepools)
                for i in range(0, sum_of_nodepools):
                    parsed_vars["node_pools"][list_of_nodepools[i]]["orchestrator_version"] = versions[i]


    data = parsed_vars
    #     # Convert to desired format
    formatted_data = convert_dict_to_format(data['node_pools'])
    modified_content = formatted_data.replace("'", '"')
    output_file_path =  str(sys.argv[1])

    with open(output_file_path, "w") as output_file:
        output_file.write("node_pools = {\n")
        output_file.write(modified_content)
        output_file.write("}")

if version_upgrade_type == "user_pool_upgrade" :
    with open(str(sys.argv[1]), 'r') as f:
        tfvars_content = f.read()
    # Parse the .tfvars content using hcl2
    parsed_vars = loads(tfvars_content)
    if version_upgrade_type == "system_pool_upgrade":
        mode_type = "System"
    else:
        mode_type = "User"
    list_of_nodepools = []
    versions = []
    list_of_nodepools = str(sys.argv[3])

    max_surge = str(sys.argv[8])
    versions = max_surge

    versions = versions.replace(" ", "")
    versions = versions.split(",")
    while ("" in versions):
        versions.remove("")
    if versions != [] :

        if list_of_nodepools == "all":
            list_of_np = [np_name for np_name, np_config in parsed_vars["node_pools"].items() if np_config["mode"] == mode_type]

            sum_of_nodepools = len(list_of_np)
            for i in range(0, sum_of_nodepools):
                if (parsed_vars["node_pools"][list_of_np[i]]["mode"]) == mode_type:
                    parsed_vars["node_pools"][list_of_np[i]]["max_surge"] = versions

        else : 
            if list_of_nodepools[0] != "all":
                list_of_nodepools = list_of_nodepools.replace(" ", "")
                list_of_nodepools = list_of_nodepools.split(",")
                while ("" in list_of_nodepools):
                    list_of_nodepools.remove("")
               
                if len(versions) != len(list_of_nodepools):
                    versions = versions[0]
                    sum_of_nodepools = len(list_of_nodepools)
                    for i in range(0, sum_of_nodepools):
                        if (parsed_vars["node_pools"][list_of_nodepools[i]]["mode"]) == mode_type:
                            parsed_vars["node_pools"][list_of_nodepools[i]]["max_surge"] = [versions] 
                else:           
                    sum_of_nodepools = len(list_of_nodepools)
                    for i in range(0, sum_of_nodepools):
                        parsed_vars["node_pools"][list_of_nodepools[i]]["max_surge"] = [versions[i]]


        data = parsed_vars
        #     # Convert to desired format
        formatted_data = convert_dict_to_format(data['node_pools'])
        modified_content = formatted_data.replace("'", '"')
        output_file_path = str(sys.argv[1])
        
        with open(output_file_path, "w") as output_file:
            output_file.write("node_pools = {\n")
            output_file.write(modified_content)
            output_file.write("}")
        print("node_pools = {\n")
        print(modified_content)
        print("}")








