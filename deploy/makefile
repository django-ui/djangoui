# set your environment variable $docker_username to get the 
PWD=${CURDIR}/
BASENAME=llmpython

# -------------------------------------------------- CREATE NW
NW=--network demonet
nw:
	docker network ls | grep demonet ; if [ "$?" != "0" ]; then docker network create demonet ; fi 
# -------------------------------------------------- DJANGO
DOCKERHUB=harbor.global.lmco.com
django_vars:
	$(eval APP=llmapp)
	$(eval PORTS=-p 8000:8000)
	$(eval TAGNAME=llmapp)
	$(eval PLATFORM="--platform=linux/amd64" )
	$(eval RUNOPTS=--rm ${PLATFORM}  --name ${APP} $(MOUNTS) $(PORTS) $(NW) $(TAGNAME) )
	$(eval IMAGE=${DOCKERHUB}:${TAGNAME})


test:
	@echo CURRENT DIRECTORY IS
	@echo ${PWD}

docker0: django_vars
	# *IMPORTANT* RUn this from base djangoui folder
	#docker pull harbor.global.lmco.com/lmc.eo.swf.lmified/ext.hub.docker.com/library/python:3.12
	docker  build  ${PLATFORM} --no-cache=true --build-arg="PWD=${PWD}" --tag=$(BASENAME) -f llmapp/deploy/docker0 .

docker1: django_vars
	# See --build-arg="password=${DJ_PASSWORD}" to modify the building
	# RUn this from 'djangoui' folder
	#make docker1 -f llmapp/deploy/makefile
	docker  build --no-cache=true  ${PLATFORM} --build-arg="PWD=${PWD}/" --build-arg="HOME=${HOME}/" --tag=llmappbase -f llmapp/deploy/docker1 .; 

docker2: django_vars
	# See --build-arg="password=${DJ_PASSWORD}" to modify the building
	#RUN this from base directory where llmapp is located
	#make docker2 -f llmapp/deploy/makefile
	cd ..; docker build --no-cache=true ${PLATFORM} --tag=${APP} -f llmapp/deploy/docker2 .

passwd: django_vars
	docker run  -u 0  -it ${RUNOPTS} passwd

run: django_vars
	docker run --rm -d  --name ${APP} $(MOUNTS) $(PORTS) $(NW) $(TAGNAME) 

# -------------------------------------------------- SSL / HTTPS
CERT_DIR=llmapp/deploy/apache
CERT=$(CERT_DIR)/sada.us.lmco.com.crt
KEY=$(CERT_DIR)/sada.us.lmco.com.key

# Run Django dev server with SSL (requires django-sslserver: pip install django-sslserver)
run_sslserver:
	python -m djangoui.manage runsslserver --certificate $(CERT) --key $(KEY) 0.0.0.0:8000

# Run with Gunicorn + SSL (production)
run_gunicorn:
	gunicorn djangoui.wsgi:application --bind 0.0.0.0:8000 --certfile=$(CERT) --keyfile=$(KEY) --workers 4

# Run Apache as HTTPS reverse proxy in Docker (Django must be running on port 8000)
run_apache:
	docker run --rm -d --name apache-ssl \
		-p 443:443 -p 80:80 \
		-v $(CERT_DIR)/default-ssl.conf:/usr/local/apache2/conf/extra/httpd-ssl.conf \
		-v $(CERT_DIR)/sada.us.lmco.com.crt:/etc/ssl/certs/sada.us.lmco.com.crt \
		-v $(CERT_DIR)/sada.us.lmco.com.key:/etc/ssl/private/sada.us.lmco.com.key \
		$(NW) httpd:2.4

it_run: django_vars
	docker run ${PLATFORM}  -u 0  --rm -it  --name ${APP} $(MOUNTS) $(PORTS) $(NW) $(TAGNAME) 'make run'

bash: django_vars
	docker run ${PLATFORM} -u 0 --rm -it  --name ${APP} $(MOUNTS) $(PORTS) $(NW) $(TAGNAME) /bin/bash

bash1: django_vars
	docker run ${PLATFORM} -u 0 --rm -it  --name base $(MOUNTS) $(PORTS) $(NW) llmapp /bin/bash

login: django_vars
	docker exec -it ${APP} bash 

stop: django_vars
	docker stop ${APP}

kill: django_vars
	docker kill ${APP}

push: django_vars
	docker tag $(TAGNAME) $(IMAGE)
	docker push $(IMAGE)
	docker tag  $(IMAGE) $(TAGNAME)

# Commit the running COPY
commit: django_vars
	@echo "Configure this and push specific images to your docker repo"
	@echo
	@echo docker commit ${APP} ${TAGNAME}
	@echo docker tag ${TAGNAME} ${IMAGE}
	@echo docker push ${IMAGE} 
	@echo 'ALL IN ONE LINE: docker commit ${APP} ${TAGNAME}; docker tag ${TAGNAME} ${IMAGE}; docker push ${IMAGE}'



# ------------------------------- TESTING MAKEFILE setting variables
test1:
	@echo "${APP}"
	@echo "${PLATFORM}"
test2:
	$(eval arch= $(shell arch))
ifeq (${arch}, arm64)
	$(eval PLATFORM="--platform=linux/amd64" )
	@echo "1..."
else
	$(eval PLATFORM= )
	@echo "2... ${arch}"
endif
	$(eval APP=django1)
	@echo "${APP}" ${arch} ${PLATFORM}

test3: test2
	@echo "${PLATFORM}"
	@echo "${APP}"
