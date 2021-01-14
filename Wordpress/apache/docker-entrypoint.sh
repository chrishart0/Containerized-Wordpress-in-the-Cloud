#!/bin/sh

webRoot='/var/www/localhost/htdocs'

#Get DB params from Parameter Store if not provided in env vars : ToDo

#Hanlde efs filesystem params
chmod 775 /var/www/localhost/htdocs
chown -R apache:apache /var/www/localhost/htdocs/wp-content/
ls -l /var/www/localhost/htdocs/wp-content/

#Call healthcheck - TODO make healthcheck page
#

#OPTIONAL: Enable troubleshooting mode
if ${TROUBLESHOOTING_MODE_ENABLED:-false}; then
    echo "WARNING! DO NOT LEAVE TROUBLESHOOTING MODE ENABLED IN PRODUCTION"
    echo "Completing troubleshooting mode setup: setting WP_DEBUG to true, making a health.html file, making a health.php file."
    sed -i -E "s/define\( 'WP_DEBUG', (.*) \)/define( 'WP_DEBUG', true )/" $webRoot/wp-config.php
    echo "Can reach a pure html page, apache healthy!" > '/var/www/localhost/htdocs/health.html'
    echo "<?php phpinfo(); ?>" > '/var/www/localhost/htdocs/health.php'
    (sleep 5; curl -f http://localhost/health.html) &
    (sleep 5; curl -f http://localhost/health.php) &
fi

#Configure DB info in wp-config
echo "Configuring wp-config.php"
sed -i "s/database_name_here/$DBNAME/" $webRoot/wp-config.php
sed -i "s/localhost/$DBHOST/" $webRoot/wp-config.php
sed -i "s/username_here/$DBUSER/" $webRoot/wp-config.php
sed -i "s/password_here/$DBUSERPASS/" $webRoot/wp-config.php

#Configure HTTPS
sed -i "/DB_COLLATE/a \
\/** SSL Settings *\/ \n\
define('FORCE_SSL_ADMIN', true);\n\
\n\
\/* Turn HTTPS 'on' if HTTP_X_FORWARDED_PROTO matches 'https' *\/ \n\
if (strpos($_SERVER['HTTP_X_FORWARDED_PROTO'], 'https') !== false)  \n\                                                                                                                        
       $_SERVER['HTTPS']='on'; " $webRoot/wp-config.php

#Launch apache
rm -rf /run/apache2/* || true && /usr/sbin/httpd -DFOREGROUND