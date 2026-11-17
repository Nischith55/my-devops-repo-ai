#!/bin/bash
set -eou pipefail

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

vers=1.6.0
# NOTE: we don't update patch versions
patch_vers=1.6.x
target_dir=${SCRIPTPATH}/${patch_vers}
mkdir -p ${target_dir}
url=https://download.elastic.co/downloads/eck/${vers}/all-in-one.yaml
output_file="${target_dir}/$(basename ${url})"
# (cd ${target_dir}; tar xzf - --wildcards '*/deploy/*.yaml' --strip-components=2)
curl -vvv -L "${url}" -o "${output_file}"
