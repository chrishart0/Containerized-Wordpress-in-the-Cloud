#bin/sh/
curl -o wordpress.tar.gz -fSL "https://wordpress.org/wordpress-${WORDPRESS_VERSION}.tar.gz"
echo "$WORDPRESS_SHA1 *wordpress.tar.gz" | sha1sum -c -
tar -xzf wordpress.tar.gz -C /tmp
rm wordpress.tar.gz