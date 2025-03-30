# How to build

--


Step 1: Pull the base image:

```
docker pull harbor.global.lmco.com/lmc.eo.swf.lmified/ext.hub.docker.com/library/python:3.12
```

Step 2:
    ```
        #cd to location of base directory djangoui
        make docker0 -f llmapp/deploy/makefile
        make docker1 -f llmapp/deploy/makefile
        #cd ..
        make docker2 -f llmapp/deploy/makefile

        make passwd -f llmapp/deploy/makefile    # <= Change password

    ```

# CAUTION

Change `PLATFORM="--platform=linux/amd64" ` in the makefile to empty for arm architecture.

-----

docker run -dit --rm --name apache -p 8080:80 -v "$PWD":/usr/local/apache2/htdocs/ httpd:2.4

============================================================================================

============================================================================================

#SINGLE SIGN ON
Login to 

https://oauthmanager.global.lmco.com/Clients/Edit/space-bitee-aries-ui

add entries 
![alt text](image.png)