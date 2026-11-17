

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
    print(modified_contents)
    with open(output_file_paths, "w") as output_files:
        output_files.write(modified_contents)

else:
    with open(str(sys.argv[1]), 'r') as f:
        tfvars_content = f.read()
    # Parse the .tfvars content using hcl2
    parsed_vars = loads(tfvars_content)
    vm_size = str(sys.argv[12])
    mode =  str(sys.argv[7])
    names = str(sys.argv[8])

    old_names_string = str(sys.argv[9])
    names = names.replace(" ", "")
    names = names.split(",")    
    orchestrationVersion= str(sys.argv[4])

    maxi = str(sys.argv[13])
    maxi = [int(val) for val in str(sys.argv[13]).split(",")]
    print(maxi)

    minimum = str(sys.argv[15])
    print("minimum",minimum)
    minimums = [int(val) for val in str(sys.argv[15]).split(",")]
    print("minimum",minimum)

    availability_count = str(sys.argv[10])
    availability_count = [int(val) for val in str(sys.argv[10]).split(",")]

    maXsurge = [str(sys.argv[6])]
    maxAvailC = int(sys.argv[11])
  
    while ("" in names):
        names.remove("")
    old_names_string = old_names_string.replace(" ", "")
    old_names_string = old_names_string.split(",")
    while ("" in old_names_string):
        old_names_string.remove("")
    list_of_vm_size = ["Standard_E4ds_v4","Standard_E32ds_v4","Standard_E8ds_v4","Standard_D4ds_v4","Standard_D4ds_v5","Standard_D8ds_v4","Standard_E4ds_v5", "Standard_D16as_v4", "Standard_E8ds_v5", "Standard_E16ds_v4"]
    for i in range(len(names)):
        az = int((i % 3) + 1)
        sz = int((i % 2) + 2)
        maxC = maxi[i % len(maxi)]
        minimumC = minimums[i % len(minimums)]
        avC = availability_count[i % len(availability_count)]

        if vm_size == 'Standard_E4ds_v4' and mode == 'System':
            yaml_data = parsed_vars
            updated_data = {
                
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[0], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':  ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' : orchestrationVersion  ,
                        'os_disk_size_gb' : 100,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' :maXsurge, #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : mode,
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }

            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "system_pool_upgrade" and i==len(names)-1:
                print(f"Formatted system_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)


        elif vm_size == 'Standard_E4ds_v4' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[0], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':  ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' : orchestrationVersion,
                        'os_disk_size_gb' : 100,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : maXsurge, #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : mode,
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }

            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])


            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)


        elif vm_size == 'Standard_E32ds_v4' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                
                
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[1], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid': ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' : orchestrationVersion,
                        'os_disk_size_gb' : 256,
                        'os_disk_type' :"Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : maXsurge, #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : mode,
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }

            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)

        elif vm_size == 'Standard_E8ds_v4' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[2], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':   ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' :orchestrationVersion,
                        'os_disk_size_gb' : 200,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : yaml_data['node_pools'][old_names_string[i]]["max_surge"], #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : yaml_data['node_pools'][old_names_string[i]]["mode"],
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }
            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)




        elif vm_size == 'Standard_D4ds_v4' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[3], 
                        'node_count': avC,
                        'enable_auto_scaling': maxC,
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':   ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' :orchestrationVersion,
                        'os_disk_size_gb' : 150,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : yaml_data['node_pools'][old_names_string[i]]["max_surge"], #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : yaml_data['node_pools'][old_names_string[i]]["mode"],
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }
            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)

        elif vm_size == 'Standard_D4ds_v5' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[4], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':  ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' : orchestrationVersion,
                        'os_disk_size_gb' : 150,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : maXsurge, #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : mode,
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }

            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)


        elif vm_size == 'Standard_D8ds_v4' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[5], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':  ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' : orchestrationVersion,
                        'os_disk_size_gb' : 256,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : maXsurge, #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : mode,
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }

            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)

        elif vm_size == 'Standard_E4ds_v5' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[6], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':  ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' : orchestrationVersion,
                        'os_disk_size_gb' : 100,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : maXsurge, #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : mode,
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }

            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)

        elif vm_size == 'Standard_D16as_v4' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[7], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':  ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' : orchestrationVersion,
                        'os_disk_size_gb' : 100,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : maXsurge, #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : mode,
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }

            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)

        elif vm_size == 'Standard_E8ds_v5' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[8], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':  ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' : orchestrationVersion,
                        'os_disk_size_gb' : 100,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : maXsurge, #set this to [] if not using this property while AKS creation
                        'zones' : yaml_data['node_pools'][old_names_string[i]]["zones"],
                        'mode' : mode,
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }

            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)

        elif vm_size == 'Standard_E16ds_v4' and mode == 'User':

            yaml_data = parsed_vars
            updated_data = {
                    names[i]: {
                        'name': names[i], 
                        'vm_size': list_of_vm_size[9], 
                        'node_count': avC,
                        'enable_auto_scaling': yaml_data['node_pools'][old_names_string[i]]["enable_auto_scaling"],
                        'enable_node_public_ip': yaml_data['node_pools'][old_names_string[i]]["enable_node_public_ip"],
                        'pod_max_pid':  ["4194304"],
                        'kubelet_disk_type' : "OS",
                        'max_count' : maxC,
                        'min_count' : minimumC,
                        'node_labels' : {
                            'balance-group' : yaml_data['node_pools'][old_names_string[i]]["node_labels"]["balance-group"]
                        },
                        'node_taints' : yaml_data['node_pools'][old_names_string[i]]["node_taints"], #this is always blank for default node pool
                        'orchestrator_version' : orchestrationVersion,
                        'os_disk_size_gb' : 256,
                        'os_disk_type' : "Ephemeral",
                        'os_type' : yaml_data['node_pools'][old_names_string[i]]["os_type"],
                        'os_sku' : yaml_data['node_pools'][old_names_string[i]]["os_sku"], #set to "Windows2019" or "Windows2022" to use windows
                        'tags' : {
                        'department' : yaml_data['node_pools'][old_names_string[i]]["tags"]["department"],
                        'description' : yaml_data['node_pools'][old_names_string[i]]["tags"]["description"],
                        'environment' : yaml_data['node_pools'][old_names_string[i]]["tags"]["environment"],
                        'financialTag' : yaml_data['node_pools'][old_names_string[i]]["tags"]["financialTag"],
                        'serviceName' : yaml_data['node_pools'][old_names_string[i]]["tags"]["serviceName"],
                        'spn' : yaml_data['node_pools'][old_names_string[i]]["tags"]["spn"]
                        },
                        'max_surge' : maXsurge, #set this to [] if not using this property while AKS creation
                        'zones' : [az],
                        'mode' : mode,
                        'cluster_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_name"],
                        'cluster_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["cluster_resource_group_name"],
                        'vnet_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_name"],
                        'snet_name' : yaml_data['node_pools'][old_names_string[i]]["snet_name"],
                        'vnet_snet_resource_group_name' : yaml_data['node_pools'][old_names_string[i]]["vnet_snet_resource_group_name"],
                        'proximity_placement_group_id' : yaml_data['node_pools'][old_names_string[i]]["proximity_placement_group_id"]
                    }
            }

            yaml_data['node_pools'].update(updated_data)
            formatted_data = convert_dict_to_format(yaml_data)
            modified_content = formatted_data.replace("'", '"')

            output_file_path = str(sys.argv[1])

            with open(output_file_path, "w") as output_file:
                output_file.write(modified_content)

            if version_upgrade_type == "user_pool_upgrade" and i==len(names)-1:
                print(f"Formatted user_pool_upgrade written to {output_file_path}")
                formatted_data = formatted_data.replace("'", '"')
                print(formatted_data)














