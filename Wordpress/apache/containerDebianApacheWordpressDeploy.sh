#/bin/bash
#This is intend for an Amazlon Linux 2 AMI
#IAM permissions needed for instance role
# - parameter store read write
#  "ssm:PutParameter",
#  "ssm:GetParameter",
#  "ssm:AddTagsToResource"

#tmux: open terminal failed: missing or unsuitable terminal: xterm-256color
#To fix this and other ssh terminal issue ad this to your path
#export TERM=xterm

############
#Parameters#
############
apacheConfigFilePath='/usr/local/apache2/conf/httpd.conf'
apacheWebDirRootPath='/usr/local/apache2/htdocs'

cd /tmp

#Download and unzip newest version of wordpress
echo "Download and unzip newest version of wordpress"
wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
rm latest.tar.gz

#Prepare to start automate config
echo "Configuring wp-config.php"
cp wordpress/wp-config-sample.php wordpress/wp-config.php

#Configure DB info
# sed -i "s/database_name_here/$wordpressDB/" wordpress/wp-config.php
# sed -i "s/username_here/$wordpressUser/" wordpress/wp-config.php
# sed -i "s/password_here/$wordpressDbUserPass/" wordpress/wp-config.php
# if [ "$useRDS" = true ];then sed -i "s/localhost/$RDSEndpoint/" wordpress/wp-config.php; fi
#ToDo set host

#Get salt values from wordpress and insert them into wp-config.php
salts=$(curl https://api.wordpress.org/secret-key/1.1/salt/)
saltsEscapedForSed=${salts//$'\n'/\\$'\n'}
sed -i "/NONCE_SALT/a $saltsEscapedForSed" wordpress/wp-config.php
sed -i '/put your unique phrase here/d' wordpress/wp-config.php

#Update the apache config to allow Wordpress permalinks and configure admin email
sed -ie '\%^<Directory "/usr/local/apache2/htdocs">%,\%^</Directory>% s/AllowOverride None/AllowOverride All/' $apacheConfigFilePath
sed -i "s|ServerAdmin root@localhost|ServerAdmin $serverAdminEmail|" $apacheConfigFilePath
#sed -i -e '$aLoadModule php7_module modules/mod_php.so' $apacheConfigFilePath

#Deploy wordpress to the web server
echo "Depoloying wordpress"
mv wordpress/* $apacheWebDirRootPath
rm -r wordpress

#Set file permissions
echo "Setting file permissions"
chown -R root $apacheWebDirRootPath
chgrp -R root $apacheWebDirRootPath
chmod 2775 $apacheWebDirRootPath
find $apacheWebDirRootPath-type d -exec chmod 2775 {} \;
find $apacheWebDirRootPath -type f -exec chmod 0664 {} \;