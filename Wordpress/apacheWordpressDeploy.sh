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
useRDS=true
serverName="arcadian.cloud"
serverAdminEmail="arcadiancloud@gmail.com"
#Each CMK costs $1/month. Use the AWS Default key and don't be lazy with your IAM perms, make them specific to the Parameterstore key
parameterStoreKeyId="alias/aws/ssm"
AWStags="Key=SiteName,Value=$serverName Key=Project,Value=Blog"
region=$(curl http://169.254.169.254/latest/meta-data/placement/availability-zone | egrep -o '(\w)+-(\w)+-[0-9]')

#Optinal RDS Parameters #ToDo write lambda function which utalizes these keys to genereate SQL user specific to this wordpress DB. Can be called from here then parameters retreived. 
RDSEndpointParameterStoreKey="/wordpress/sharedDB/Root/Endpoint"
RDSRootUserParameterStoreKey="/wordpress/sharedDB/Root/User"
RDSRootPasswordParameterStoreKey="/wordpress/sharedDB/Root/Pass"

###########################

#ToDo check that all needed parameters are provided 

#consider using "set -e" this will error the whole script on any failure

#Handle DB Users and Passwords
#If no openssl use something like this:  cat /dev/urandom | tr -dc "A-Za-z0-9*+\-.,&%$!@^;~" | head -c14;
echo "Genereating random database name, passwords, users"
wordpressDB=("${serverName//.}$RANDOM")
wordpressUser=("${serverName//.}$RANDOM")
wordpressDbUserPass=$(openssl rand -base64 12)
if [ "$useRDS" = true ];then 
    echo "using RDS"
else #Handle using local DB
    echo "using local db"
    rootDbUserPass=$(openssl rand -base64 12) 
    
fi

function ssmParameterFailure {
    printf "aws ssm command failed. Please correct the issue and try again. \nExiting..."
    exit 1
}



echo "Installing JQ for parameter handling"
sudo yum install -y jq

#Store DB passwords in parameter store
#Parameter store standard is free, use it to your heart's content https://aws.amazon.com/systems-manager/pricing/
# || after each ssm put-parameter only runs if there was some issue storing the parameter. It is very important to fail out if a parameter fails to get stored.
#First check for parameter store permissions, if no parameter store permissions and no flag then exit
#ToDo: Too much repition, see if this whole thing can be made into a function
echo "Storing parameters in Parameter store"
aws ssm put-parameter --name /wordpress/$serverName/info/serverName --value $serverName --type SecureString --key-id $parameterStoreKeyId --tags $AWStags --tier Standard --region $region --no-overwrite || ssmParameterFailure
aws ssm put-parameter --name /wordpress/$serverName/info/serverAdminEmail --value $serverAdminEmail --type SecureString --key-id $parameterStoreKeyId --tags $AWStags --tier Standard --region $region --no-overwrite || ssmParameterFailure

if [ "$useRDS" = true ];then
    #ToDo genereate local user and pass
    aws ssm put-parameter --name /wordpress/$serverName/db/rds/wordpressDB --value $wordpressDB --type SecureString --key-id $parameterStoreKeyId --tags $AWStags --tier Standard --region $region --no-overwrite || ssmParameterFailure
    aws ssm put-parameter --name /wordpress/$serverName/db/rds/wordpressUser --value $wordpressUser --type SecureString --key-id $parameterStoreKeyId --tags $AWStags --tier Standard --region $region --no-overwrite || ssmParameterFailure
    aws ssm put-parameter --name /wordpress/$serverName/db/rds/wordpressDBUserPass --value $wordpressDbUserPass --type SecureString --key-id $parameterStoreKeyId --tags $AWStags --tier Standard --region $region --no-overwrite || ssmParameterFailure
    RDSEndpoint=$(aws ssm get-parameter --name $RDSEndpointParameterStoreKey --with-decryption --region $region | jq '.Parameter.Value' | sed -e 's/^"//' -e 's/"$//') || ssmParameterFailure
    rootDbUserUser=$(aws ssm get-parameter --name $RDSRootUserParameterStoreKey --with-decryption --region $region | jq '.Parameter.Value' | sed -e 's/^"//' -e 's/"$//') || ssmParameterFailure
    rootDbUserPass=$(aws ssm get-parameter --name $RDSRootPasswordParameterStoreKey --with-decryption --region $region | jq '.Parameter.Value' | sed -e 's/^"//' -e 's/"$//') || ssmParameterFailure
else
    aws ssm put-parameter --name /wordpress/$serverName/db/local/wordpressDB --value $wordpressDB --type SecureString --key-id $parameterStoreKeyId --tags $AWStags --tier Standard --region $region --no-overwrite || ssmParameterFailure
    aws ssm put-parameter --name /wordpress/$serverName/db/local/wordpressUser --value $wordpressUser --type SecureString --key-id $parameterStoreKeyId --tags $AWStags --tier Standard --region $region --no-overwrite || ssmParameterFailure
    aws ssm put-parameter --name /wordpress/$serverName/db/local/wordpressDBUserPass --value $wordpressDbUserPass --type SecureString --key-id $parameterStoreKeyId --tags $AWStags --tier Standard --region $region --no-overwrite || ssmParameterFailure
    aws ssm put-parameter --name /wordpress/$serverName/db/local/rootDbUserPass --value $rootDbUserPass --type SecureString --key-id $parameterStoreKeyId --tags $AWStags --tier Standard --region $region --no-overwrite || ssmParameterFailure
fi

###############################
#Configure Dirs for future use#
###############################
echo "Setting up needed directories"
sudo mkdir /backups/ /logs/ /scripts/
sudo chgrp ec2-user -R /logs/ /scripts/ /backups/
sudo chmod 770 -R /logs/ /scripts/ /backups/

####################
#Install LAMP Stack#
####################

#This section was based on the below AWS documenation.
#https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-lamp-amazon-linux-2.html

echo "Installing updates and needed packages" 

#Update the server. -y confirms package updates
sudo yum update -y
sudo yum upgrade -y

#Use the amazon-linux-extras repo to install mariadb and php
sudo amazon-linux-extras install -y php7.2
sudo yum install -y httpd php-gd php-fpm mod_ssl mod_http2 php-pecl-imagick #ImageMagick

#Start apache service and set to atuostart
echo "Starting Apache2"
sudo systemctl start httpd
sudo systemctl enable httpd

#############################################
#Install and configure CloudWatch Monitoring#
#############################################
#Start Cron for scheduling commands
echo "Starting Crond"
sudo systemctl start crond
sudo systemctl enable crond

echo "Installing and configuring Cloudwatch metrics"
#https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/mon-scripts.html
sudo yum install -y perl-Switch perl-DateTime perl-Sys-Syslog perl-LWP-Protocol-https perl-Digest-SHA.x86_64
curl https://aws-cloudwatch.s3.amazonaws.com/downloads/CloudWatchMonitoringScripts-1.2.2.zip -O
unzip CloudWatchMonitoringScripts-1.2.2.zip
rm CloudWatchMonitoringScripts-1.2.2.zip
mv aws-scripts-mon /scripts/
echo "*/5 * * * * ec2-user /scripts/aws-scripts-mon/mon-put-instance-data.pl --mem-util --mem-used --disk-space-util --disk-path=/ --from-cron" | sudo tee -a /etc/crontab

#################################
#Install and Configure Wordpress#
#################################
#Install and configure Wordpress. This section based on the below AWS documenation
#https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/hosting-wordpress.html


if [ "$useRDS" = true ];then
    #Install mysql so the tooling can be used to remotly connect
    sudo yum install -y mysql

    #ToDo add test to confrim DB connectivity
    #mysql -u $rootDbUserUser --password="$rootDbUserPass" -h $RDSEndpoint -e "SHOW DATABASES;"

    #Configure RDS MySQL with new user
    mysql -u $rootDbUserUser --password="$rootDbUserPass" -h $RDSEndpoint -e "CREATE USER '$wordpressUser'@'%' IDENTIFIED BY '$wordpressDbUserPass';"
    mysql -u $rootDbUserUser --password="$rootDbUserPass" -h $RDSEndpoint -e "CREATE DATABASE $wordpressDB;"
    mysql -u $rootDbUserUser --password="$rootDbUserPass" -h $RDSEndpoint -e "GRANT ALL PRIVILEGES ON $wordpressDB.* TO '$wordpressUser'@'%';"
    mysql -u $rootDbUserUser --password="$rootDbUserPass" -h $RDSEndpoint -e "FLUSH PRIVILEGES;"
else
    #Install MariaDB
    sudo amazon-linux-extras install -y lamp-mariadb10.2-php7.2
    sudo yum install -y mariadb-server

    #Startup the DB and set it to run on startup
    echo "Starting MariaDB"
    sudo systemctl start mariadb
    sudo systemctl enable mariadb

    #Configure root user password
    echo "Setting up DB"
    mysql -u root --password="" -e "SET PASSWORD FOR 'root'@'localhost' = PASSWORD('$rootDbUserPass');"

    #Configure MariaDB
    mysql -u root --password="$rootDbUserPass" -e "CREATE USER '$wordpressUser'@'localhost' IDENTIFIED BY '$wordpressDbUserPass';"
    mysql -u root --password="$rootDbUserPass" -e "CREATE DATABASE $wordpressDB;"
    mysql -u root --password="$rootDbUserPass" -e "GRANT ALL PRIVILEGES ON $wordpressDB.* TO '$wordpressUser'@localhost"
    mysql -u root --password="$rootDbUserPass" -e "FLUSH PRIVILEGES;"
fi

#Download and unzip newest version of wordpress
echo "Download and unzip newest version of wordpress"
wget https://wordpress.org/latest.tar.gz
tar -xzf latest.tar.gz
rm latest.tar.gz

#Configure DB info
echo "Configuring wp-config.php"
cp wordpress/wp-config-sample.php wordpress/wp-config.php
sed -i "s/database_name_here/$wordpressDB/" wordpress/wp-config.php
sed -i "s/username_here/$wordpressUser/" wordpress/wp-config.php
sed -i "s/password_here/$wordpressDbUserPass/" wordpress/wp-config.php
if [ "$useRDS" = true ];then sed -i "s/localhost/$RDSEndpoint/" wordpress/wp-config.php fi
#ToDo set host

#Get salt values from wordpress and insert them into wp-config.php
salts=$(curl https://api.wordpress.org/secret-key/1.1/salt/)
saltsEscapedForSed=${salts//$'\n'/\\$'\n'}
sed -i "/NONCE_SALT/a $saltsEscapedForSed" wordpress/wp-config.php
sed -i '/put your unique phrase here/d' wordpress/wp-config.php

#Update the apache config to allow Wordpress permalinks and configure admin email
sudo sed -ie '\%^<Directory "/var/www/html">%,\%^</Directory>% s/AllowOverride None/AllowOverride All/' /etc/httpd/conf/httpd.conf
sudo sed -i "s|ServerAdmin root@localhost|ServerAdmin $serverAdminEmail|" /etc/httpd/conf/httpd.conf

#Deploy wordpress to the web server
echo "Depoloying wordpress"
sudo mv wordpress/* /var/www/html/
rm -r wordpress

#Set file permissions
echo "Setting file permissions"
sudo chown -R apache /var/www
sudo chgrp -R apache /var/www
sudo chmod 2775 /var/www
find /var/www -type d -exec sudo chmod 2775 {} \;
find /var/www -type f -exec sudo chmod 0664 {} \;

#Restart Apache to pickup config changes
sudo systemctl restart httpd 

#Test that server is working
echo "Testing Site"
$siteTest=$(curl localhost/wp-admin/install.php)
if [ -z $siteTest ];then {
    echo "Deployment has finished and wordpress is ready for human configuration"
} else {
    echo "ERROR: Deployment was not sucesful! Cannot reach localhost/wp-admin/install.php"
}
fi
