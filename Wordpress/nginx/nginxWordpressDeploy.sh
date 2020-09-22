#/bin/bash
#This is intend for an Amazon Linux 2 AMI
#Run this script after initialWordpressDeploy.sh

############
#Parameters#
############
serverName="kgdevops.cloud"
serverAdminEmail="kgdevops3@gmail.com"

#####################
#HTTPS Configuration#
#####################
#Generate an SSL cert with certbot. Thanks EFF!
#https://certbot.eff.org/lets-encrypt/pip-nginx
#https://certbot.eff.org/docs/using.html#certbot-commands

wget https://dl.eff.org/certbot-auto
sudo mv certbot-auto /usr/local/bin/certbot-auto
sudo chown root /usr/local/bin/certbot-auto
sudo chmod 0755 /usr/local/bin/certbot-auto

#Configure certbot
echo "rsa-key-size = 4096" | sudo tee -a /etc/letsencrypt/config.ini > /dev/null
echo "email = $serverAdminEmail" | sudo tee /etc/letsencrypt/config.ini > /dev/null

#sudo certbot certonly --webroot -w /var/www/html -d $serverName --config /etc/letsencrypt/config.ini --agree-tos --non-interactive
sudo /usr/local/bin/certbot-auto --nginx -w /var/www/html -d $serverName --config /etc/letsencrypt/config.ini --agree-tos --non-interactive --no-bootstrap

#Auto renew
echo "0 0 0 1 * ? * root /usr/local/bin/certbot-auto renew -q" | sudo tee -a /etc/crontab > /dev/null

#Restart nginx to pickup config changes
sudo systemctl restart nginx

#Test https works
curl https://$serverName