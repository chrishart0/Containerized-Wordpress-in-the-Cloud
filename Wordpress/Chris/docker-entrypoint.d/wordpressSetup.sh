#bin/sh/
mkdir /wordpress/ && cd /wordpress/
curl -o wordpress.tar.gz -fSL "https://wordpress.org/wordpress-${WORDPRESS_VERSION}.tar.gz"
echo "$WORDPRESS_SHA1 *wordpress.tar.gz" | sha1sum -c -
tar -xzf wordpress.tar.gz
rm wordpress.tar.gz

