# Build and Test Instructions

First, make sure you are in the directory with the Dockerfile then run the following script

## To start with a fresh database each time

 - Note that usernames and passwords used here are not secure, this is just for local testing of the container.
 - Note that there is a docker container run command commented out, use that one intead if you want to source your web root locally
```
dbRootPass="4cRM79rw3YLedPTt"

#Start DB container
docker kill mysql #Remove this because it keeps causing issues
docker rm mysql #Remove this because it keeps causing issues
docker run --name mysql -p 3306:3306 --net=bridge -e MYSQL_ROOT_PASSWORD=$dbRootPass -e MYSQL_DATABASE=wpdb -d mysql
sleep 15

#Setup DB and User
mysql -u root --password=$dbRootPass -h 127.0.0.1 -e "CREATE USER 'wordpressUser'@'%' IDENTIFIED BY 'wordpressDbUserPass';"
mysql -u root --password=$dbRootPass -h 127.0.0.1 -e "ALTER USER 'wordpressUser'@'%' IDENTIFIED WITH mysql_native_password BY 'wordpressDbUserPass';"
mysql -u root --password=$dbRootPass -h 127.0.0.1 -e "CREATE DATABASE wptest;"
mysql -u root --password=$dbRootPass -h 127.0.0.1 -e "GRANT ALL PRIVILEGES ON wptest.* TO 'wordpressUser'@'%';"
mysql -u root --password=$dbRootPass -h 127.0.0.1 -e "FLUSH PRIVILEGES;"

##################
#Configure WP with the right DB IP
dbIP=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' mysql)
sed -i -E "s/'DB_HOST', '(.*)'/'DB_HOST', '$dbIP'/" app/wp-config.php

docker build -t apache-wordpress .

#Start Web server container
#docker container run  -p 80:80 --net=bridge -v "$(pwd)"/app:/usr/local/apache2/htdocs -v "$(pwd)"/conf:/usr/local/apache2/conf apache-wordpress
docker container run -p 80:80 -it -e DBNAME=wptest -e DBHOST=$dbIP -e DBUSER=wordpressUser -e DBUSERPASS=wordpressDbUserPass apache-wordpress
```

## To connect to a running container use the below command but change out <container name> with the container's name
```
docker exec -it <container name> sh
```

## Manually push a dockerfile to ECR for testing purposes
* To get your proper commands go to ECR, select your repo, and click View push commands
* If not using a default profile, don't forget to add a --profile
```
#Just replace this with your commands from ecr
aws ecr get-login-password --region <region>  | docker login --username AWS --password-stdin <account number>.dkr.ecr.<region>.amazonaws.com
docker tag apache-wordpress:latest  <account number>.dkr.ecr.<region>.amazonaws.com/wordpress
docker push <account number>.dkr.ecr.<region>.amazonaws.com/wordpress

#Force 
aws ecs update-service --force-new-deployment --service <service name> --cluster <cluster name>
```