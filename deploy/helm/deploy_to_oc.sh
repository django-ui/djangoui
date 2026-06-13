#!/bin/bash

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HELM_DIR="$REPO_ROOT/helm"

# 1. Login to OpenShift
oc login --token=sha256~bBBm2vaf5xZlLDtW6z8RLfoOOlztBJ5AVtqjD2l88J4 --server=https://api.ocp-ugw1-dev.ecs.us.lmco.com:6443

# 2. Lint the chart
helm lint "$HELM_DIR/charts/ontology-experiment" --values "$HELM_DIR/values/dev.yaml" --debug

# 3. Dry run
helm upgrade ontology-experiment-dev "$HELM_DIR/charts/ontology-experiment" \
  --install --values "$HELM_DIR/values/dev.yaml" --dry-run --debug

# 4. Deploy
helm upgrade ontology-experiment-dev "$HELM_DIR/charts/ontology-experiment" \
  --install --values "$HELM_DIR/values/dev.yaml" --wait --debug
