#bin/sh/
cd /tmp
curl -o wordpress.tar.gz -fSL "https://wordpress.org/wordpress-${WORDPRESS_VERSION}.tar.gz"
echo "$WORDPRESS_SHA1 *wordpress.tar.gz" | sha1sum -c -
tar -xzf wordpress.tar.gz
rm wordpress.tar.gz

#Delete default index.html
rm $WEB_DIR/index.html
cp -r /tmp/wordpress/* $WEB_DIR

#Set Permissions
chown -R nginx $WEB_DIR
chgrp -R nginx $WEB_DIR
chmod 2775 $WEB_DIR

#Start php handler
#php-fpm7