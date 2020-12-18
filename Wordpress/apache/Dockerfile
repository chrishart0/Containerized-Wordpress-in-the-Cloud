
# ┏━━━┓╋╋╋╋╋┏┓╋╋╋╋╋╋┏━━━┓┏┓
# ┗┓┏┓┃╋╋╋╋╋┃┃╋╋╋╋╋╋┃┏━━┛┃┃
# ╋┃┃┃┣━━┳━━┫┃┏┳━━┳━┫┗━━┳┫┃┏━━┓
# ╋┃┃┃┃┏┓┃┏━┫┗┛┫┃━┫┏┫┏━━╋┫┃┃┃━┫
# ┏┛┗┛┃┗┛┃┗━┫┏┓┫┃━┫┃┃┃╋╋┃┃┗┫┃━┫
# ┗━━━┻━━┻━━┻┛┗┻━━┻┛┗┛╋╋┗┻━┻━━┛

FROM httpd:2.4
LABEL Author="ChristianHart"

COPY containerDebianApacheWordpressDeploy.sh /usr/bin
COPY docker-entrypoint.sh /usr/bin

RUN chmod +x /usr/bin/containerDebianApacheWordpressDeploy.sh \
    && chmod +x /usr/bin/docker-entrypoint.sh


RUN apt-get update && apt-get upgrade \
    && apt-get -y install curl default-mysql-client fontconfig-config fonts-dejavu-core libaio1 \
        libao-common libao4 libapache2-mod-php libapache2-mod-php7.3 libflac8 libfontconfig1 libfreetype6  \
        libgd3 libgdbm-compat4 libgpm2 libjbig0 libjpeg62-turbo libjs-cropper libjs-prototype libjs-scriptaculous \
        libmagic-mgc libmagic1 libmariadb3 libncurses6 libogg0 libpcre2-8-0 libperl5.28 libpng16-16 libprocps7 \
        libreadline5 libsnappy1v5 libsodium23 libspeex1 libsqlite3-0 libterm-readkey-perl libtiff5 libvorbis0a \
        libvorbisenc2 libvorbisfile3 libwebp6 libx11-6 libx11-data libxau6 libxcb1 libxdmcp6 libxpm4 netbase \
        openssl php-common php-gd php-getid3 php-mysql php7.3-common php7.3-gd php7.3-json php7.3-mysql \
        php7.3-opcache php7.3-readline procps psmisc readline-common \
        wget


WORKDIR /usr/local/apache2

#HEALTHCHECK --interval=3m --timeout=3s \
#  CMD curl -f http://localhost/index.php || exit 1

CMD ["/usr/bin/docker-entrypoint.sh"]

EXPOSE 80 443
