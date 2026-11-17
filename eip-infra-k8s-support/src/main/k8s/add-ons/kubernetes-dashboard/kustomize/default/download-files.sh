#!/bin/bash
set -eou pipefail

SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"

# vers -> tagname
vers=v2.0.5
target_dir=${SCRIPTPATH}/base
url=https://github.com/kubernetes/dashboard/tarball/${vers}

# NOTE: always check the wildcard and strip-components in case the remote
# repo has been reorganized
curl -L ${url} | (cd ${target_dir}; \
  tar xzf - --wildcards '*/aio/deploy/recommended/*.yaml' --strip-components=4)
