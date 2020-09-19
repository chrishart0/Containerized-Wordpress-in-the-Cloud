#Build and Test Instructions

#Make sure you are in the directoru with the Dockerfile and run the following commands
docker build -t container-wordpress .
docker run -p 80:80 -t container-wordpress

#To connect to a running container use the below command but change out <container name> with the container's name
docker exec -it <container name> sh