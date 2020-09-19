#Build and Test Instructions

docker build -t container-wordpress .
docker run -i -p 443:443 -v-t container-wordpress
docker exec -it /bin/sh