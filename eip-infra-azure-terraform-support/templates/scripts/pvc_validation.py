#!/usr/bin/python
import os
import subprocess
import json
import ast
import yaml
import sys
import time
from datetime import date
def get_pvc_details():
    """This function checks whether the post-upgrade.txt file is present before and after the rollout of kubecost-cost-analyzer pod. If not then troubleshooting will be required further validations should be stopped
    """
    print("checking the kubecost-cost-analyzer pvc is present or not")
    try:
        kubecost_check = subprocess.run(['kubectl get ns kubecost'], capture_output=True, shell=True)
        kubecost_check1 = kubecost_check.stdout.decode('utf-8')
        if kubecost_check.returncode != 1 and len(kubecost_check1) != 0:
            today = date.today()
            kca = subprocess.check_output(["kubectl" " -n" " kubecost" " get" " pvc" " kubecost-cost-analyzer"], shell=True)
            kca1 = kca.decode('utf-8')
            print(kca1)
            if kca1 != "":
                kcapod = subprocess.check_output(["kubectl" " -n" " kubecost" " get" " pods" " |" " grep" " -i" " kubecost-cost-analyzer*" " |" " awk" " '{printf $1}'"], shell=True)
                kcapod1 = kcapod.decode('utf-8')
                print(kcapod1)
                print("checking the file post-upgrade is presnt on kubecost-cost-analyzer pod. If present then it will be deleted and recreated again")
                subprocess.run(['kubectl exec -n kubecost %s -- touch "/var/configs/post-upgrade-file.txt"'%(kcapod1)], shell=True, capture_output=True)
                kcapuf = subprocess.run(['kubectl exec -n kubecost %s -- ls -lrt /var/configs/post-upgrade-file.txt'%(kcapod1)], shell=True, capture_output=True)
                # kcapuf1 = kcapuf.decode('utf-8')
                print(kcapuf.returncode)
                if kcapuf.returncode != 0:
                    subprocess.check_output(["kubectl" " exec" " -n" " kubecost" " %s" " --" " rm /var/configs/post-upgrade-file.txt"%(kcapod1)], shell=True)
                subprocess.check_output(["kubectl" " exec" " -n" " kubecost" " %s" " --" " touch \"/var/configs/post-upgrade-file-%s.txt\""%(kcapod1,today)], shell=True)
                # kcapuf1 = kcapuf.decode('utf-8')
                # print(kcapuf1)
                print("kubecost-cost-analyzer deployment will be restarted after the file creation and the status of the file will be checked again")
                subprocess.check_output(["kubectl" " -n" " kubecost" " rollout" " restart" " deployment" " kubecost-cost-analyzer"], shell=True)
                time.sleep(120)
                kcapod = subprocess.check_output(["kubectl" " -n" " kubecost" " get" " pods" " |" " grep" " -i" " kubecost-cost-analyzer*" " |" " awk" " '{printf $1}'"], shell=True)
                kcapod1 = kcapod.decode('utf-8')
                print(kcapod1)
                print("The file should be present after rollout of the deployment. If not then we will have to hault the deployment")
                kcapuf = subprocess.check_output(["kubectl" " exec" " -n" " kubecost" " %s" " --" " ls -lrt \"/var/configs/post-upgrade-file-%s.txt\""%(kcapod1,today)], shell=True)
                kcapuf1 = kcapuf.decode('utf-8')
                kcapuf1 = ""
                print(kcapuf1)
                if kcapuf1 != "":
                    print("pvc validation successful")
                else:
                    print("pvc validation is not successful. Please troubleshoot the issue")
            else:
                print("kubecost-cost-analyzer is not present on this cluster. Skipping pvc validations on this cluster")
    except subprocess.CalledProcessError as kubecostexc:
        print("error code", kubecostexc.returncode)
        # else:
        #     print("kubecost is not installed on this cluster")

def appd_validation():
    """This function checks whether appd pod is having the java agent running successfully"""
    print("viewing configMap appd-agent-config")
    appdConfigMap = subprocess.check_output(["kubectl" " get" " configmaps" " -A" " |" " grep" " -i" " appd-agent-config" " |" " awk" " '{printf $1}'"], shell=True)
    appdConfigMap1 = appdConfigMap.decode('utf-8')    
    print(appdConfigMap1)
    print("selecting a deployment using APPDYNAMICS")
    appdochdepl = subprocess.run(['kubectl get deployment -n %s -o=json | jq -r \'.items[] | select(.spec.template.spec.containers[0].env[].name == \"APPDYNAMICS_AGENT_APPLICATION_NAME\") | .metadata.name \''%(appdConfigMap1)], shell=True, capture_output=True)
    appdochdepl2 = appdochdepl.stdout.decode('ASCII').strip()
    print("checking the logs of the pods of APPDYNAMICS deployment to see Java status")
    if appdochdepl2 != "":
        appdochdepl2 = appdochdepl.stdout.decode('ASCII')
        appdochdepl2 = list(appdochdepl2.split("\n"))
        print(type(appdochdepl2))
        print(len(appdochdepl2))
        appdochpod = subprocess.check_output(["kubectl" " get" " pods" " -n" " %s" " |" " grep" " -i" " %s" " |" " awk" " '{print $1}'"%(appdConfigMap1,appdochdepl2[0])], shell=True)
        appdochpod1 = appdochpod.decode('utf-8')
        print(appdochpod1)
        appdochpod1list = list(appdochpod1.split("\n"))
        print(type(appdochpod1list))
        print(appdochpod1list)
        appdpodjavastatus = subprocess.check_output(["kubectl" " -n" " %s" " logs" " %s" " |" " grep" " -i" " success"%(appdConfigMap1,appdochpod1list[0])], shell=True)
        appdpodjavastatus1 = appdpodjavastatus.decode('utf-8')
        print(appdpodjavastatus1)
    else:
        print("appd is not present on this cluster. So skipping appd validation")

def msi_acr_pullbinding():
    """This function deletes the msi_acr_pullbinding and recreates it from the backup taken"""
    department = sys.argv[1]
    build = sys.argv[2]
    directory = sys.argv[3]
    cluster = sys.argv[4]
    print(build)
    print(department)
    print(directory)
    print(cluster)
    print("checking the namespace for acrpullbinding for the pep-%s-ops-admin")
    msiacr = subprocess.check_output(["kubectl" " get" " acrpullbinding" " -A" " |" " grep" " -i" " pep-%s-ops-admin" " |" " awk" " '{print $1}'"%(department)], shell=True)
    msiacr1 = msiacr.decode('utf-8')
    print(msiacr1)
    listing_backup = subprocess.check_output(["ls" " -lrt" " %s"%(directory)], shell=True)
    listing1_backup = listing_backup.decode('utf-8')
    print(listing1_backup)
    if msiacr1 != "":
        msiacr1list = list(msiacr1.split("\n"))
        print(type(msiacr1list))
        print(msiacr1list)
        print("checking the pods in the namespace")
        msiacrpods = subprocess.check_output(["kubectl" " -n" " %s" " get" " pods"%(msiacr1list[0])], shell=True)
        msiacrpods1 = msiacrpods.decode('utf-8')
        print(msiacrpods1)
        msiacr1list = list(msiacr1.split("\n"))
        print(type(msiacr1list))
        print(msiacr1list)
        print("checking the secrets in the namespace")
        msiacrsecrets = subprocess.check_output(["kubectl" " -n" " %s" " get" " secrets"%(msiacr1list[0])], shell=True)
        msiacrsecrets1 = msiacrsecrets.decode('utf-8')
        print(msiacrsecrets1)
        print("checking the acrpullbinding in the namespace")
        msiacr_list = subprocess.check_output(["kubectl" " -n" " %s" " get" " acrpullbinding"%(msiacr1list[0])], shell=True)
        msiacr_list1 = msiacr_list.decode('utf-8')
        print(msiacr_list1)
        print("checking the acrpullbinding in the namespace")
        msiacr_list = subprocess.check_output(["kubectl" " -n" " %s" " get" " acrpullbinding" " --output=custom-columns='NAME:.metadata.name'" " --no-headers" " |" " awk" " '{print $1}'"%(msiacr1list[0])], shell=True)
        msiacr_list1 = msiacr_list.decode('utf-8')
        print(msiacr_list1)
        print("taking the acrpullbinding backup")
        backup_acr_pullbinding = subprocess.check_output(["kubectl" " -n" " %s" " get" " acrpullbinding" " -o=yaml" " >" " %s/acr_pullbinding_backup_%s.yml"%(msiacr1list[0],directory,build)], shell=True)
        backup_acr_pullbinding1 = backup_acr_pullbinding.decode('utf-8')
        print(backup_acr_pullbinding1)    
        listing_backup = subprocess.check_output(["ls" " -lrt" " %s"%(directory)], shell=True)
        listing1_backup = listing_backup.decode('utf-8')
        print(listing1_backup)
        msiacr_deletion = subprocess.check_output(["kubectl" " -n" " %s" " delete" " acrpullbinding" " %s"%(msiacr1list[0],msiacr_list1)], shell=True)
        msiacr_deletion1 = msiacr_deletion.decode('utf-8')
        print(msiacr_deletion1)
        msiacr_creation = subprocess.check_output(["kubectl" " -n" " %s" " create" " -f" " %s/acr_pullbinding_backup_%s.yml"%(msiacr1list[0],directory,build)], shell=True)
        msiacr_creation1 = msiacr_creation.decode('utf-8')
        print(msiacr_creation1)
        msiacr_list = subprocess.check_output(["kubectl" " -n" " %s" " get" " acrpullbinding" " --output=custom-columns='NAME:.metadata.name'" " --no-headers" " |" " head" " -1"%(msiacr1list[0])], shell=True)
        msiacr_list1 = msiacr_list.decode('utf-8')
        print(msiacr_list1)
        msiacrsecrets_post_creation = subprocess.check_output(["kubectl" " -n" " %s" " get" " secrets"%(msiacr1list[0])], shell=True)
        msiacrsecrets_post_creation1 = msiacrsecrets_post_creation.decode('utf-8')
        print(msiacrsecrets_post_creation1)
    else:
        print("msi_acr_pullbinding is not present on this cluster. Skipping msi_acr_pullbinding on this cluster")

def conjur():
    """This function checks the conjur job and takes backup of the yaml file and recreates it using the backup file"""
    department = sys.argv[1]
    print(department)
    build = sys.argv[2]
    # build = "1927533"
    print(build)
    f_job = f"pep-{department}-conjur-agent-job"
    print("listing the jobs running")
    try:
        # conjur = subprocess.check_output(["kubectl" " get" " job" " -A" " --output=custom-columns='NAMESPACE:.metadata.namespace','NAME:.metadata.name'" " --no-headers"], shell=True)
        conjur = subprocess.run(['kubectl get job123 -A --output=custom-columns=\'NAMESPACE:.metadata.namespace\',\'NAME:.metadata.name\' --no-headers'], capture_output=True, shell=True)
        print("**********************")
        print(conjur)
        conjur2 = conjur.stdout.decode('utf-8')
        print(conjur2)
        print("**********************")
        if conjur.returncode != 1 and len(conjur2) != 0:
            print("code successful")
            # if conjur != 'None':
            conjur = subprocess.check_output(["kubectl" " get" " job" " -A" " --output=jsonpath='{range .items[*]}{.metadata.namespace',.metadata.name}{\"\\n\"}{end}'"], shell=True)
            conjur = subprocess.check_output(["kubectl" " get" " job" " -A" " -o=json"], shell=True)
            conjur1 = conjur.decode('utf-8')
            conjur1 = conjur1.strip()
            print(conjur1)
            print(type(conjur1))
            conjurlist = list(conjur1.split("\n"))
            print(conjurlist)
            conjur_dict_new = {}
            print("listing the conjur job in a dictionary")
            for i in range(0,len(conjurlist)):
                conjur_sublist = (list(conjurlist[i].split()))
                conjur_dict = {conjur_sublist[j]: conjur_sublist[j + 1] for j in range(0,1) if conjur_sublist[j + 1] == f_job }
                conjur_dict_new.update(conjur_dict)
            print(conjur_dict_new)
            for key, value in conjur_dict_new.items():
                conjur_namespace_job = subprocess.check_output(["kubectl" " -n" " %s" " get" " job" " %s"%(key,value)], shell=True)
                conjur_namespace_job1 = conjur_namespace_job.decode('utf-8')
                print(conjur_namespace_job1)
                print("taking backup of the conjur job")
                backup_conjur_job = subprocess.check_output(["kubectl" " -n" " %s" " get" " job" " %s" " -o=yaml" " >" " conjur_job_backup_%s.yml"%(key,value,build)], shell=True)
                backup_conjur_job1 = backup_conjur_job.decode('utf-8')
                print("deleting the conjur job")
                conjur_job_deletion = subprocess.check_output(["kubectl" " -n" " %s" " delete" " job" " %s"%(key,value)], shell=True)
                conjur_job1 = conjur_job_deletion.decode('utf-8')
                print(conjur_job1)
                print("removing the uid references from the conjur job backup file")
                with open('conjur_job_backup_%s.yml'%(build), 'r') as file:
                    conjur_job_yaml = yaml.safe_load(file)
                print(conjur_job_yaml['spec']['template']['metadata']['labels'])
                print(conjur_job_yaml['spec']['selector'])
                print(type(conjur_job_yaml))
                del conjur_job_yaml['spec']['template']['metadata']['labels']['controller-uid']
                del conjur_job_yaml['spec']['selector']
                with open('conjur_job_backup_%s.yml'%(build), 'w') as file:
                    yaml.dump(conjur_job_yaml, file)
                print("creating the conjur job from the backup file")
                conjur_job_creation = subprocess.check_output(["kubectl" " create" " -f" " conjur_job_backup_%s.yml"%(build)], shell=True)
                conjur_job1 = conjur_job_creation.decode('utf-8')
                print(conjur_job1)
                time.sleep(120)
                print("validating the status of conjur job")
                conjur_job_list = subprocess.check_output(["kubectl" " -n" " %s" " get" " job" " %s"%(key,value)], shell=True)
                conjur_job_list1 = conjur_job_list.decode('utf-8')
                print(conjur_job_list1)
                print("validating the status of conjur job")
                try:
                    conjur_job_list = subprocess.check_output(["kubectl" " -n" " %s" " wait" " --for=condition=complete" " --timeout=180s" " job/%s"%(key,value)], shell=True)
                except subprocess.CalledProcessError as grepexc:
                    print("error code", grepexc.returncode)
                    if grepexc.returncode == 1:
                        print("conjur job validation failed")
                        conjurjobpod = subprocess.check_output(["kubectl" " -n" " %s" " get" " pod" " |" " grep" " -i" " \"pep-eiap-conjur-agent-job-*\"" " |" " awk" " '{printf $1}'"%(key)], shell=True)
                        conjurjobpod1 = conjurjobpod.decode('utf-8')
                        print(conjurjobpod1)
                        subprocess.run(['kubectl -n %s logs %s > %slog.txt'%(key,conjurjobpod1,conjurjobpod1)], shell=True)
                # conjur_job_list1 = conjur_job_list.stderr.decode('utf-8')
                # conjur_job_list1 = conjur_job_list.stdout.decode('utf-8')
                break
            # else:
            #     print("conjur job not present on this cluster. Skipping conjur job validation on this cluster")
        else:
            print("conjur is not installed on this cluster")
    except subprocess.CalledProcessError as conjurexc:
        print("error code", conjurexc.returncode)

if __name__== "__main__":
    get_pvc_details()
    appd_validation()
    msi_acr_pullbinding()
    conjur()

