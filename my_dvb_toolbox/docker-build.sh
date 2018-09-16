#!/bin/bash



# build plain
docker build -t mumudvb:cam    . -f -
# remove #cam; patterns from Dockerfile, build mumudvb with cam/scam support
sed -r 's_^#(cam|scam);__g' Dockerfile      | docker build -t mumudvb:cam    . -f -
# remove #tool; patterns from Dockerfile, build everything (Swiss-Army-Knife)
sed -r 's_^#(cam|scam|tool);__g' Dockerfile | docker build -t mumudvb:sak    . -f -

# verify
# no CAM support
docker run --rm -it mumudvb:simple mumudvb | grep CAM
# with CAM support
docker run --rm -it mumudvb:cam mumudvb | grep CAM
# with w_scan installed as well
docker run --rm -it mumudvb:simple w_scan -v