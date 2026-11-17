#!/bin/bash
set -eou pipefail

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

out_dir_name=2.4.1
vers=release-2.4
target_dir=${SCRIPTPATH}/${out_dir_name}/base
url=https://github.com/kubernetes/kube-state-metrics/tarball/${vers}


curl -L ${url} | (cd ${target_dir}; tar xzf - --wildcards '*/examples/standard' --strip-components=3)
