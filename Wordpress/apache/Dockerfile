#PHP Images can be found at https://hub.docker.com/_/php/
FROM php:7.3-alpine3.12

#Copy WP files to file system
COPY app/ /var/www/localhost/htdocs/

#Concatenated RUN commands
RUN apk add --update apache2 php7-apache2 php7-mbstring php7-session php7-json php7-pdo php7-openssl php7-common php7-mysqli \
        php7-tokenizer php7-pdo php7-pdo_mysql php7-xml php7-simplexml php7-iconv php7-gd php7-curl php7-imap php7-cgi fcgi \
        php7-soap php7-xmlrpc php7-posix php7-mcrypt php7-gettext php7-ldap php7-ctype php7-dom \
    && sed -i '/LoadModule rewrite_module/s/^#//g' /etc/apache2/httpd.conf \
    && sed -i '/LoadModule session_module/s/^#//g' /etc/apache2/httpd.conf \
    && sed -i 's/AllowOverride\ None/AllowOverride\ All/g' /etc/apache2/httpd.conf \
    && docker-php-ext-install pdo_mysql \
    && rm  -rf /tmp/* /var/cache/apk/*

#Write apache logs to console - https://serverfault.com/questions/711168/writing-apache2-logs-to-stdout-stderr
RUN ln -sf /proc/self/fd/1 /var/log/apache2/access.log && \
    ln -sf /proc/self/fd/1 /var/log/apache2/error.log

#Delete unneeded leftover index.html
RUN rm /var/www/localhost/htdocs/index.html

#Launch the httpd in foreground
CMD rm -rf /run/apache2/* || true && /usr/sbin/httpd -DFOREGROUND