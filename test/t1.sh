#!/bin/bash
if [ "$#" != 1 ]; then
    iterations=1
else
    iterations=$1
fi
for (( a=0; a < $iterations; a++ )); do echo "====== iter: $a"; time http_proxy=localhost:8080 curl http://urlinfo/1/www.google.com:80/testing1234?bar; done
