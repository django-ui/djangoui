  ## Openshift
    -   Get your token from openshift (click name > copy login command)
    -   run login command in terminal/command (oc login ...)
    -   cd into the helm dir (has [your]-chart and values folders)

oc login --token=sha256~bBBm2vaf5xZlLDtW6z8RLfoOOlztBJ5AVtqjD2l88J4 --server=https://api.ocp-ugw1-dev.ecs.us.lmco.com:6443


  ## Helm
    cd helm/
    helm lint charts/ontology-experiment --values ./values/dev.yaml --debug
    #Dry run
    helm upgrade ontology-experiment-dev charts/ontology-experiment --install --values ./values/dev.yaml --dry-run --debug
    #Ready to deploy manually
    helm upgrade ontology-experiment-dev charts/ontology-experiment --install --values ./values/dev.yaml --wait --debug
    #Uninstall
    helm uninstall ontology-experiment-dev