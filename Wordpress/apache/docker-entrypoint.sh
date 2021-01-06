#!/bin/sh
echo "test"
chmod 775 /var/www/localhost/htdocs
chown -R apache:apache /var/www/localhost/htdocs/wp-content/
ls -l /var/www/localhost/htdocs/wp-content/
rm -rf /run/apache2/* || true && /usr/sbin/httpd -DFOREGROUND