# flame-archive-exporter

the dockerfile here will build a container that runs the python script inside this repo.

the kubernetes yaml here will stand up a usable deployment of the exporter with all secrets management and service monitoring included.

start dev service with `skaffold dev --port-forward`

helm chart in the `helm` folder, deployed with fluxcd