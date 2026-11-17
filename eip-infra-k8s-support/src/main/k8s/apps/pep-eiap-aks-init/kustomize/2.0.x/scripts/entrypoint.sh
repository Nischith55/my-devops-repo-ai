#!/usr/bin/env bash
set -euo pipefail
# ##
# Setup the Node Changes.
# - involves setting up ssh into nodes
# - copy all necessary files.
# ##
# IMPORTANT:
# - Please be extremely careful since this is a daemonset and any
#   error will do a redeployment, so watch for duplicated.
# - EVERY command must be checked for errors, if you cop out using
#   || true, then ensure idempotency where required.
#: ##
# This should already be passed in container env else default
ROOT_MOUNT_DIR="${ROOT_MOUNT_DIR}"
# add to node admin user [NOTE: defaults to neipi002]
ADMIN_USER="${AKS_ADMIN_USER}"
# where our config map files are
PROJECTED_DIR="${PROJECTED_MOUNT_DIR}"

# ##
# - setup ssh hack
# ##
setup_ssh_node() {
  # Step 1. copy private key to home_dir of this pods user context
  ssh_dir=~/.ssh
  mkdir -p ${ssh_dir}
  chmod 0700 ${ssh_dir}
  cp -pf ${PROJECTED_DIR}/id_rsa_0 ${ssh_dir}/id_rsa || echo "Failed to copy [id_rsa_0]"
  cp -pf ${PROJECTED_DIR}/id_rsa_0.pub ${ssh_dir}/id_rsa.pub || echo "Failed to copy [id_rsa_0.pub]"

  # Step 2. Copy to node admin use pub key
  admin_ssh_dir="${ROOT_MOUNT_DIR}/home/${ADMIN_USER}/.ssh"
  node_auth_keys_file=${admin_ssh_dir}/authorized_keys
  node_auth_keys_file_orig=${admin_ssh_dir}/authorized_keys.ORIG
  # make a backup
  if [[ ! -f "${node_auth_keys_file_orig}" ]]; then
    cp -pn ${node_auth_keys_file} ${node_auth_keys_file_orig} || echo "Failed copy: [${node_auth_keys_file_orig}]"
  fi

  # Step 3. append public key if not present.
  pub_key_0=$(cat ${PROJECTED_DIR}/id_rsa_0.pub)
  # now, append authorized_keys on the node
  if ! grep -q -F "${pub_key_0}" "${node_auth_keys_file}"; then
    echo "Adding public key to [${node_auth_keys_file}]"
    echo ${pub_key_0} >> "${node_auth_keys_file}"
  fi
  return 0
}
#


# ##
# Copy PepsiCo CA Certs
# IMPORTANT:
# - in Ubuntu bionic and lower /usr/local/share/ca-certificates will
#   be picked up by update-ca-certificates command
# ##
copy_pep_ca_certs() {
  cacert_dir=${ROOT_MOUNT_DIR}/usr/local/share/ca-certificates
  # just in case
  mkdir -p "${cacert_dir}" || echo "Failed to create directory [${cacert_dir}]"
  cp -pf ${PROJECTED_DIR}/PepsiCoRootCA.crt "${cacert_dir}/PepsiCoRootCA.crt" || echo Failed to copy [PepsiCoRootCA.crt]
  cp -pf ${PROJECTED_DIR}/PepsiCoCA01.crt "${cacert_dir}/PepsiCoCA01.crt" || echo Failed to copy [PepsiCoCA01.crt]
  return 0
}

# ##
# Copy limits
# ##
copy_limits_conf() {
  # remove old ones one if it exists
  local old_files=${PROJECTED_DIR}/zz-eiap-limits.conf
  local f conf_file
  for _f in $old_files; do
    if [[ -e ${_f} ]]; then
      rm -f ${_f}
    fi
  done
  conf_file=${PROJECTED_DIR}/zzz-eiap-limits.conf
  cp -pf ${conf_file} ${ROOT_MOUNT_DIR}/etc/security/limits.d/${conf_file}
  return 0
}

##
# Copy timesyncd conf
##
copy_timesyncd_conf() {
  local conf_filename=timesyncd.conf
  local timesyncd_conf=${ROOT_MOUNT_DIR}/etc/systemd/${conf_filename}
  local backup_file=${ROOT_MOUNT_DIR}/etc/systemd/timesyncd.conf.aks-orig
  local pod_conf_path
  if [[ ! -r ${backup_file} ]]; then
    cp -p ${timesyncd_conf} ${backup_file}
  fi
  pod_conf_path=${PROJECTED_DIR}/timesyncd.conf
  cp -pf ${pod_conf_path} ${timesyncd_conf} || echo "Failed copy: [${timesyncd_conf}] -> [${pod_conf_path}]"
  return 0
}

##
# Copy sysctl
##
copy_sysctl_conf() {
  local conf_filename=zzz-sysctl-aks-eiap.conf
  local node_sysctl_file=${ROOT_MOUNT_DIR}/etc/sysctl.d/${conf_filename}
  local pod_conf_path=${PROJECTED_DIR}/${conf_filename}
  cp -pf ${pod_conf_path} ${node_sysctl_file} || echo "Failed copy: [${pod_conf_path}] -> [${node_sysctl_file}]"
  return 0
}

## Apply the changes
apply_changes() {
  # ##
  # Now we copy the ubuntu apply changes script to the NODE
  # ##
  cp -pf ${PROJECTED_DIR}/apply-node-changes.sh ${ROOT_MOUNT_DIR}/tmp/apply-node-changes.sh || echo "Failed copy: [${apply-node-changes.sh}]"
  echo "Done setup for node change script"

  # -- Apply the changes by ssh'ing

  ssh -l "${ADMIN_USER}" -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null ${NODE_IP} "sudo /tmp/apply-node-changes.sh" || echo "ERROR: Failed to apply changes"
}

setup_ssh_node || echo "ERROR: non-zero return status setup_ssh_node()"
copy_pep_ca_certs || echo "ERROR: non-zero return status copy_pep_ca_certs()"
copy_limits_conf || echo "ERROR: non-zero return status copy_limits_conf()"
copy_timesyncd_conf || echo "ERROR: non-zero return status copy_timesyncd_conf()"
copy_sysctl_conf || echo "ERROR: non-zero return status copy_sysctl_conf()"
apply_changes || echo "ERROR: non-zero return status"
exit 0
