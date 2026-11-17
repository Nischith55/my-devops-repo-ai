#!/usr/bin/env bash
set -euo pipefail
# ##
# IMPORTANT:
# - This is designed to run on the NODE and NOT the pod make sure you can
#   ssh from the pod to run the script
# - Also, this script should be "scp'ed" OR copied by the initContainer to
#   the NODE filesystem
# - This must be run as sudo
# ##

DEBIAN_FRONTEND=noninteractive
export DEBIAN_FRONTEND

# ##
# reload all sysctl settings in ubuntu
# ##
echo "---------- START: reload sysctl --------"
custom_sysctl_file=/etc/sysctl.d/zzz-sysctl-aks-eiap.conf
if [[ -r "${custom_sysctl_file}" ]]; then
  echo "Applying [${custom_sysctl_file}]"
  /sbin/sysctl --load="${custom_sysctl_file}" || echo "Failed sysctl load"
else
  echo "WARNING: [${custom_sysctl_file}] file not found.."
fi
echo "---------- END: reload sysctl --------"

# ##
# Make sure /etc/ssl/certs/ca-certificates.crt is updated
# ##
echo "---------- START: configure PepsiCo CA Certs --------"
# Check whether pepsico cacerts are already in the bundle
pep_certs=$(ls /etc/ssl/certs | awk '/PepsiCoRootCA/ || /PepsiCoCA01/' | wc -l)
if [[ "${pep_certs}" == "2" ]]; then
  echo "pepsico cacerts already available; Skipping cacert update block"
else
  # install ca certificates
  cacert_log=/tmp/cacert-update.log
  echo "updating ca certificates"
  update-ca-certificates > $cacert_log
  # Capture the number of certs added and removed into variables
  added_certs=$(cat $cacert_log | head -2 | tail -1 | awk '{print $1, $3}' | awk '{print $1}')
  removed_certs=$(cat $cacert_log | head -2 | tail -1 | awk '{print $1, $3}' | awk '{print $2}')
  # Check for cacert addition/removal and restart containerd
  if [[ "$added_certs" > "0" || "$removed_certs" > "0" ]]; then
    echo "$added_certs pepsico cacerts added to the bundle, $removed_certs removed; restarting containerd"
    # restart containerd
    systemctl restart containerd || echo "restart containerd failed"
    echo "succesfully restarted containerd"
  else
    echo "no certificates added/removed; skipping containerd restart"
  fi
fi
echo "---------- END: configure PepsiCo CA Certs --------"

# ##
# restart timesyncd
# ##

echo "---------- START: restart timesyncd --------"
systemctl restart systemd-timesyncd || echo "Failed to restart timesyncd"
echo "---------- END: restart timesyncd --------"

# ##
# Install and update packages...
# ##

echo "---------- START: apt disable autoupgrade  --------"

# # NOTE: uncomment below if u ever get messed up with lock files
# if lockfile_pids=$(lsof -t /var/lib/dpkg/lock-frontend 2>/dev/null); then
#   echo "  ++ Appears we have lockfile in use"
#   for _p in $lockfile_pids; do
#     kill -9 ${_p} || echo "Failed to kill process [${_p}]"
#   done
# fi
# rm -f /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock /var/lib/apt/lists/lock /var/cache/apt/archives/lock
# dpkg --configure -a

pkg_mgr="apt-get -qq -y --no-install-recommends "

echo "~~ Disabling auto-update..."
${pkg_mgr} purge unattended-upgrades || echo "unattended-upgrades purge failed"
echo "~~ Disable auto-update done ..."

echo "---------- END: apt disable autoupgrade  --------"

# echo "---------- START: apt dist upgrade  --------"
# echo "~~ Updating apt cache..."
# ${pkg_mgr} update || echo "update failed.."
# echo "~~ Done Updating apt cache.."

# echo "Performing dist-upgrade"
# dpkg_options="-o \"Dpkg::Options::=--force-confdef\" -o \"Dpkg::Options::=--forceconfold\" "
# ${pkg_mgr} $dpkg_options dist-upgrade || echo "dist-upgrade failed"
# echo "~~ Done Performing dist-upgrade"
# echo "---------- END: apt dist upgrade  --------"

# ##
# Cleanup motd
# ##

upgrade_file=/var/lib/ubuntu-release-upgrader/release-upgrade-available
if [[ -r "${upgrade_file}" ]]; then
  truncate -s 0 "${upgrade_file}" || echo "Failed to truncate [${upgrade_file}]"
fi
echo "Done: applying changes"
exit 0
