
# ┏━━━┓╋╋╋╋╋┏┓╋╋╋╋╋╋┏━━━┓┏┓
# ┗┓┏┓┃╋╋╋╋╋┃┃╋╋╋╋╋╋┃┏━━┛┃┃
# ╋┃┃┃┣━━┳━━┫┃┏┳━━┳━┫┗━━┳┫┃┏━━┓
# ╋┃┃┃┃┏┓┃┏━┫┗┛┫┃━┫┏┫┏━━╋┫┃┃┃━┫
# ┏┛┗┛┃┗┛┃┗━┫┏┓┫┃━┫┃┃┃╋╋┃┃┗┫┃━┫
# ┗━━━┻━━┻━━┻┛┗┻━━┻┛┗┛╋╋┗┻━┻━━┛

FROM nginx:mainline-alpine
LABEL Author="ChristianHart,DanielS1996"

ENV WORDPRESS_VERSION 5.5.1
ENV WORDPRESS_SHA1 d3316a4ffff2a12cf92fde8bfdd1ff8691e41931

#Install needed packages
RUN apk update \
    && apk add --no-cache php7-common php7-iconv php7-json php7-gd php7-curl php7-xml php7-mysqli php7-imap php7-cgi fcgi php7-pdo php7-pdo_mysql php7-soap php7-xmlrpc php7-posix php7-mcrypt php7-gettext php7-ldap php7-ctype php7-dom

#WORKDIR "/www"
#RUN make /app
COPY entrypoint.sh /entrypoint.sh

COPY index.html /usr/share/nginx/html/index.html

CMD ["/entrypoint.sh"]

HEALTHCHECK --interval=30s --timeout=3s \
  CMD curl -f http://localhost/ || exit 1

EXPOSE 80
