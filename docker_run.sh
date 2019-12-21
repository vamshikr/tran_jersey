#! /bin/bash

function main {
    docker build -f Dockerfile -t vamshikrb/agilis-chems-webapp:latest . && \
        docker run --rm -it --env-file ./env.conf -p 8080:8080 vamshikrb/agilis-chems-webapp:latest
}

main $@
