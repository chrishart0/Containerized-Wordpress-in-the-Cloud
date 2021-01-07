#!/bin/sh

webRoot='/var/www/localhost/htdocs'

#Get DB params from Parameter Store if not provided in env vars : ToDo

#Hanlde efs filesystem params
chmod 775 /var/www/localhost/htdocs
chown -R apache:apache /var/www/localhost/htdocs/wp-content/
ls -l /var/www/localhost/htdocs/wp-content/

#Call healthcheck - TODO make healthcheck page
#(sleep 5; curl -f http://localhost/health.php) &

#Configure DB info in wp-config
echo "Configuring wp-config.php"
sed -i "s/database_name_here/$DBNAME/" $webRoot/wp-config.php
sed -i "s/localhost/$DBHOST/" $webRoot/wp-config.php
sed -i "s/username_here/$DBUSER/" $webRoot/wp-config.php
sed -i "s/password_here/$DBUSERPASS/" $webRoot/wp-config.php

#Launch apache
rm -rf /run/apache2/* || true && /usr/sbin/httpd -DFOREGROUND