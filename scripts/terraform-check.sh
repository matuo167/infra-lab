#!/usr/bin/env bash
set -euo pipefail

terraform -chdir=terraform/local fmt -check -recursive
terraform -chdir=terraform/aws fmt -check -recursive
terraform -chdir=terraform/local init -backend=false
terraform -chdir=terraform/local validate
terraform -chdir=terraform/aws init -backend=false
terraform -chdir=terraform/aws validate
