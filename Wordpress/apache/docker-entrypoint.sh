#!/bin/sh

webRoot='/var/www/localhost/htdocs'
efsLocation='/var/www/localhost/htdocs/wp-content/'

#Hanlde efs filesystem params
#echo "Adding EFS permissions"
#chown -R apache:apache $efsLocation
#chmod 775 $efsLocation

#Workaround for efs not letting wordpress create new dirs in root
#themes
if [ -d "$webRoot/wp-content/themes/" ]; then
    echo "$webRoot/wp-content/themes/ exists."
else
    echo "Creating $webRoot/wp-content/themes/"
    /bin/su -s /bin/sh -c "mkdir $webRoot/wp-content/themes/" apache
fi

#plugins
if [ -d "$webRoot/wp-content/plugins/" ]; then
    echo "$webRoot/wp-content/plugins/ exists."
else
    echo "Creating $webRoot/wp-content/plugins/"
    /bin/su -s /bin/sh -c "mkdir $webRoot/wp-content/plugins/" apache
fi


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
    echo "ls -l $webRoot"
    ls -l $webRoot
    echo "ls -l $webRoot/wp-content/"
    ls -l $webRoot/wp-content/
    echo "ls -l $webRoot/wp-content/uploads/"
    ls -l $webRoot/wp-content/uploads/

    #Tester write permissions to EFS
    echo "Testing write permissions of root to wp-content"
    touch $webRoot/wp-content/test
    if test -f "$webRoot/wp-content/test"; then
        ls -l $webRoot/wp-content/test
        echo "$webRoot/wp-content/test exists, passed write perms test."
    else
        echo "ERROR: $webRoot/wp-content/test does not exists, failed write perms test!"
    fi
    rm $webRoot/wp-content/test

    echo "Testing write permissions of root to wp-content"
    mkdir $webRoot/wp-content/wp-test/
    touch $webRoot/wp-content/wp-test/test
    if test -f "$webRoot/wp-content/test"; then
        ls -l $webRoot/wp-content/test
        echo "$webRoot/wp-content/test exists, passed write perms test."
    else
        echo "ERROR: $webRoot/wp-content/test does not exists, failed write perms test!"
    fi
    rm $webRoot/wp-content/wp-test/test

    echo "Testing write permissions of apache to wp-content"
    /bin/su -s /bin/sh -c "touch $webRoot/wp-content/test2" apache
    if test -f "$webRoot/wp-content/test2"; then
        ls -l $webRoot/wp-content/test2
        echo "$webRoot/wp-content/test2 exists, passed write perms test."
    else
        echo "ERROR: $webRoot/wp-content/test does not exists, failed write perms test!"
    fi
    rm $webRoot/wp-content/test2

    echo "Testing write permissions of apache to wp-content"
    /bin/su -s /bin/sh -c "mkdir $webRoot/wp-content/wp-test2/" apache
    /bin/su -s /bin/sh -c "touch $webRoot/wp-content/wp-test2/test2" apache
    if test -f "$webRoot/wp-content/wp-test2/test2"; then
        ls -l $webRoot/wp-content/wp-test2/test2
        echo "$webRoot/wp-content/wp-test2/test2 exists, passed write perms test."
    else
        echo "ERROR: $webRoot/test does not exists, failed write perms test!"
    fi
    rm $webRoot/wp-content/wp-test2/test2

    #Check running processes every 10 seconds
    # (while true; do
    #     sleep 10
    #     ps aux
    # done) &


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