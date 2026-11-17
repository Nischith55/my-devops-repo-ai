import sys
loc = str(sys)
from hcl2 import loads
import json
from hcl2 import loads
import json



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


            # elif key == "node_zones":
            #     if not value:
            #         result += " " * indent + f"{key} = [] \n"
            #     else:
            #         result += " " * indent + f"{key} = {value} \n"

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
        # elif isinstance(value, bool):
        #     result += " " * indent + f"{key} = {str(value).lower()}\n"
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

        else:
            result += " " * indent + f"{key} = \"{value}\"\n"
    return result


with open(str(sys.argv[1]), 'r') as f:
    tfvars_content = f.read()

parsed_vars = loads(tfvars_content)


old_nodepools = []
av = []
old_nodepools = str(sys.argv[9])
print("this are old np",old_nodepools)
av   = str(sys.argv[10])
print("this is the availability count which will be assigned as max value",av)
mini =  str(sys.argv[14])
print("this is min value will be assignd as min value",mini)

old_nodepools = old_nodepools.replace(" ", "")
old_nodepools = old_nodepools.split(",")
while ("" in old_nodepools):
    old_nodepools.remove("")

av = av.replace(" ", "")
av = av.split(",")
while ("" in av):
    av.remove("")


mini = mini.replace(" ", "")
mini = mini.split(",")
while ("" in mini):
    av.remove("")

if len(old_nodepools) == len(av) == len(mini):

    for i in range(0, len(old_nodepools)):
            parsed_vars["node_pools"][old_nodepools[i]]["max_count"] = 1 if int(av[i]) == 0 else int(av[i])
            parsed_vars["node_pools"][old_nodepools[i]]["min_count"] = int(mini[i])
            # if int(av[i]) == 0:
            #     parsed_vars["node_pools"][old_nodepools[i]]["enable_auto_scaling"] = False
            


    data = parsed_vars
    #     # Convert to desired format
    formatted_data = convert_dict_to_format(data['node_pools'])
    modified_content = formatted_data.replace("'", '"')

    output_file_path = str(sys.argv[1])

    with open(output_file_path, "w") as output_file:
        output_file.write("node_pools = {\n")
        output_file.write(modified_content)
        output_file.write("}")

    print(f"Formatted data written to {output_file_path}")

    print("node_pools = {")
    print(formatted_data)
    print("}")

else:
    print("length of nodepools , av , mini is not matching with eac other")


