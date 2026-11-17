#!/bin/bash
set -eou pipefail

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

vers=v1.22.1
vers_dir=1.22.x
target_dir=${SCRIPTPATH}/${vers_dir}
mkdir -p ${target_dir}
url=https://github.com/jaegertracing/jaeger-operator/tarball/${vers}
#url=https://github.com/kubernetes/kube-state-metrics/tarball/${vers}

# (cd ${target_dir}; tar xzf - --wildcards '*/deploy/*.yaml' --strip-components=2)
curl -vvv -L ${url} | (cd ${target_dir}; tar xzf - --wildcards '*/deploy/*.yaml' --strip-components=2)
