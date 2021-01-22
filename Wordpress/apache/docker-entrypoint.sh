#!/bin/sh

webRoot='/var/www/localhost/htdocs'
efsLocation='/var/www/localhost/htdocs/wp-content/'

#Hanlde efs filesystem params
echo "Adding EFS permissions"
chown -R apache:apache $efsLocation
chmod 775 $efsLocation

#Configure DB info in wp-config
echo "Configuring wp-config.php"
sed -i "s/database_name_here/$DBNAME/" $webRoot/wp-config.php
sed -i "s/localhost/$DBHOST/" $webRoot/wp-config.php
sed -i "s/username_here/$DBUSER/" $webRoot/wp-config.php
sed -i "s/password_here/$DBUSERPASS/" $webRoot/wp-config.php

#OPTIONAL: Enable troubleshooting mode
if ${TROUBLESHOOTING_MODE_ENABLED:-false}; then
    echo "WARNING! DO NOT LEAVE TROUBLESHOOTING MODE ENABLED IN PRODUCTION"

    ##############################
    ### File Permissions tests ###

    #Show permissions of used directories
    ls -l $webRoot
    ls -l $webRoot/wp-content/
    ls -l $webRoot/wp-content/uploads/

    #Tester write permissions in various places
    echo "Testing write permissions to wp-content"
    touch $webRoot/test
    if test -f "$webRoot/test"; then
        echo "$webRoot/test exists, passed write perms test."
    else
        echo "ERROR: $webRoot/test does not exists, failed write perms test!"
    fi
    rm $webRoot/test

    echo "Testing write permissions to wp-content"
    touch $webRoot/wp-content/test
    if test -f "$webRoot/wp-content/test"; then
        echo "$webRoot/wp-content/test exists, passed write perms test."
    else
        echo "ERROR: $webRoot/wp-content/test does not exists, failed write perms test!"
    fi
    rm $webRoot/wp-content/test
    ##############################

    ########################
    ### Web server Tests ###
    echo "Completing troubleshooting mode setup: setting WP_DEBUG to true, making a health.html file, making a health.php file."
    sed -i -E "s/define\( 'WP_DEBUG', (.*) \)/define( 'WP_DEBUG', true )/" $webRoot/wp-config.php
    echo "Can reach a pure html page, apache healthy!" > '/var/www/localhost/htdocs/health.html'
    echo "<?php phpinfo(); ?>" > '/var/www/localhost/htdocs/health.php'
    (sleep 5; curl -f http://localhost/health.html) &
    ########################
fi

#Setup WP-Config to handle HTTPS offloading at the ELB
sed -i "/DB_COLLATE/a \
\/** SSL Settings *\/ \n\
define('FORCE_SSL_ADMIN', true);\n\
\n\
\/** Turn HTTPS 'on' if HTTP_X_FORWARDED_PROTO matches 'https' *\/ \n\
if (strpos(\$_SERVER['HTTP_X_FORWARDED_PROTO'], 'https') !== false) { \n\
    \$_SERVER['HTTPS'] = 'on'; \n\
} " wp-config.php

#Launch apache
rm -rf /run/apache2/* || true && /usr/sbin/httpd -DFOREGROUND