docker network ls | grep demonet ; if [ "$?" != "0" ]; then docker network create demonet ; fi
#docker run -d -p 80:80 -p 443:443 --network demonet --rm --name apache apache-ssl-local 
export IMAGE='harbor.us.lmco.com/lmc.space.ai/apache-ssl:latest'
export OPT='--add-host=host.docker.internal:host-gateway'
docker run --rm -d -p 80:80 -p 443:443 --network demonet --name apache $OPT $IMAGE