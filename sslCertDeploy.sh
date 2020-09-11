#/bin/bash
#This is intend for an Amazlon Linux 2 AMI
#Run this script after initialWordpressDeploy.sh

############
#Parameters#
############
serverName="arcadian.cloud"
serverAdminEmail="arcadiancloud@gmail.com"

#####################
#HTTPS Configuration#
#####################
#Generate an SSL cert with certbot. Thanks EFF!
#https://certbot.eff.org/lets-encrypt/centosrhel8-apache.html
#https://certbot.eff.org/docs/using.html#certbot-commands

sudo amazon-linux-extras install epel -y
sudo yum install certbot -y

#Configure certbot
echo "rsa-key-size = 4096" | sudo tee -a /etc/letsencrypt/config.ini > /dev/null
echo "email = $serverAdminEmail" | sudo tee /etc/letsencrypt/config.ini > /dev/null

sudo certbot certonly --webroot -w /var/www/html -d $serverName --config /etc/letsencrypt/config.ini --agree-tos --non-interactive

#Auto renew
echo "0 0,12 * * * root python3 -c 'import random; import time; time.sleep(random.random() * 3600)' && sudo certbot renew -q" | sudo tee -a /etc/crontab > /dev/null

#Configure SSL keys locations
fullchainLocation=$(echo /etc/letsencrypt/live/$serverName/fullchain.pem | awk '{print "'\''" $0 "'\''"}')
privkeyLocation=$(echo /etc/letsencrypt/live/$serverName/privkey.pem | awk '{print "'\''" $0 "'\''"}')
chainLocation=$(echo /etc/letsencrypt/live/$serverName/chain.pem | awk '{print "'\''" $0 "'\''"}')

sudo sed -i "s|SSLCertificateFile /etc/pki/tls/certs/localhost.crt|SSLCertificateFile $fullchainLocation|" /etc/httpd/conf.d/ssl.conf
sudo sed -i "s|SSLCertificateKeyFile /etc/pki/tls/private/localhost.key|SSLCertificateKeyFile $privkeyLocation|" /etc/httpd/conf.d/ssl.conf
sudo sed -i "s|#SSLCertificateChainFile /etc/pki/tls/certs/server-chain.crt|SSLCertificateChainFile $chainLocation|" /etc/httpd/conf.d/ssl.conf

#General Setup
sudo sed -i "s|#ServerName www.example.com:443|ServerName $serverName:443|" /etc/httpd/conf.d/ssl.conf
sudo sed -i "s|ServerAdmin root@localhost|ServerAdmin $serverAdminEmail|" /etc/httpd/conf/httpd.conf

#Configure staping for less ssl load https://httpd.apache.org/docs/2.4/ssl/ssl_howto.html
SSLStaplingConfig="
SSLUseStapling On
SSLStaplingCache 'shmcb:logs/ssl_stapling(32768)'
"
SSLStaplingConfig=${SSLStaplingConfig//$'\n'/\\$'\n'}
sudo sed -i "/Listen 80/a $SSLStaplingConfig" /etc/httpd/conf/httpd.conf

#Configure https redirect
HTTPSRedirectConfig="
Listen 80
<VirtualHost *:80>
  ServerName $serverName
  Redirect permanent / https://$serverName/
</VirtualHost>
"
HTTPSRedirectConfig=${HTTPSRedirectConfig//$'\n'/\\$'\n'}
sudo sed -i "s|Listen 80|$HTTPSRedirectConfig|" /etc/httpd/conf/httpd.conf

#Restart apache to pickup config changes
sudo systemctl restart httpd

#Test https works
curl https://$serverName