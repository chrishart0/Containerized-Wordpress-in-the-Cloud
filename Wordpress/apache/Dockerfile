# PHP Images can be found at https://hub.docker.com/_/php/
FROM php:7.3-alpine3.12

# The application will be copied in /home/application and the original document root will be replaced in the apache configuration 
#COPY app /home/application/ 

# Concatenated RUN commands
RUN apk add --update apache2 php7-apache2 php7-mbstring php7-session php7-json php7-pdo php7-openssl php7-tokenizer php7-pdo php7-pdo_mysql php7-xml php7-simplexml\
    && sed -i '/LoadModule rewrite_module/s/^#//g' /etc/apache2/httpd.conf \
    && sed -i '/LoadModule session_module/s/^#//g' /etc/apache2/httpd.conf \
    && sed -i 's/AllowOverride\ None/AllowOverride\ All/g' /etc/apache2/httpd.conf \
    && docker-php-ext-install pdo_mysql \
    && rm  -rf /tmp/* /var/cache/apk/*

# Launch the httpd in foreground
CMD rm -rf /run/apache2/* || true && /usr/sbin/httpd -DFOREGROUND