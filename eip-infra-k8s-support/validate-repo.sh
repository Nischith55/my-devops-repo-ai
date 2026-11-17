#!/usr/bin/env bash

set -u -o pipefail

errors=0
warnings=0
strict=0

if [[ "${1:-}" == "--strict" ]]; then
  strict=1
fi

echo "Running repository validation checks..."

# 1) Ensure README references match existing docs.
required_docs=(
  "README-PY3-ANSIBLE4.md"
  "README-PY2-ANSIBLE29.md"
)

for doc in "${required_docs[@]}"; do
  if [[ ! -f "$doc" ]]; then
    echo "ERROR: Missing required setup doc: $doc"
    errors=$((errors + 1))
  fi
done

if grep -Eq "README-PY3-ANSIBLE211\.md|README-PY2-ANSIBLE299\.md" README.md; then
  echo "ERROR: README.md contains stale setup file references."
  errors=$((errors + 1))
fi

# 2) Validate shell script syntax for tracked shell files.
while IFS= read -r sh_file; do
  if ! bash -n "$sh_file"; then
    echo "ERROR: Shell syntax failed: $sh_file"
    errors=$((errors + 1))
  fi
done < <(git ls-files "*.sh")

# 3) Warn on tracked key/cert artifacts.
for sensitive_file in final-key.txt final-cert.txt; do
  if git ls-files --error-unmatch "$sensitive_file" >/dev/null 2>&1; then
    echo "WARNING: Potentially sensitive tracked file: $sensitive_file"
    warnings=$((warnings + 1))
  fi
done

echo "Validation summary: errors=$errors warnings=$warnings"

if (( errors > 0 )); then
  exit 1
fi

if (( strict == 1 && warnings > 0 )); then
  exit 2
fi

echo "Repository validation passed."
