FROM nginx:mainline-alpine
LABEL Author="ChristianHart"

ENV WORDPRESS_VERSION 5.5.1
ENV WORDPRESS_SHA1 d3316a4ffff2a12cf92fde8bfdd1ff8691e41931
ENV WEB_DIR /usr/share/nginx/html

#Install needed packages
RUN apk update \
    && apk add php7-fpm php7-mcrypt php7-soap php7-openssl php7-gmp php7-pdo_odbc php7-json php7-dom php7-pdo php7-zip php7-mysqli php7-sqlite3 php7-apcu php7-pdo_pgsql php7-bcmath php7-gd php7-odbc php7-pdo_mysql php7-pdo_sqlite php7-gettext php7-xmlreader php7-xmlrpc php7-bz2 php7-iconv php7-pdo_dblib php7-curl php7-ctype

COPY Configs/nginx-default.conf /etc/nginx/conf.d/default.conf
COPY Configs/php-wordpress_pool.conf /etc/php7/php-fpm.conf
COPY docker-entrypoint.d/ /docker-entrypoint.d/

#HEALTHCHECK --interval=3m --timeout=3s \
#  CMD curl -f http://localhost/index.php || exit 1
CMD [ "/bin/sh" ]
#CMD ["nginx", "-g", "daemon off;"] 

EXPOSE 80
