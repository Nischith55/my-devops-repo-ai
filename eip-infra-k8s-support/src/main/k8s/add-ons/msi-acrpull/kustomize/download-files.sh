#!/bin/bash
set -eou pipefail

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

out_dir_name=default
vers=main
target_dir=${SCRIPTPATH}/${out_dir_name}/base
url=https://github.com/Azure/msi-acrpull/tarball/${vers}

curl -L ${url} | (cd ${target_dir}; tar xzf - --wildcards '*/deploy/latest' --strip-components=3)
