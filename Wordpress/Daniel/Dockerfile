
# ┏━━━┓╋╋╋╋╋┏┓╋╋╋╋╋╋┏━━━┓┏┓
# ┗┓┏┓┃╋╋╋╋╋┃┃╋╋╋╋╋╋┃┏━━┛┃┃
# ╋┃┃┃┣━━┳━━┫┃┏┳━━┳━┫┗━━┳┫┃┏━━┓
# ╋┃┃┃┃┏┓┃┏━┫┗┛┫┃━┫┏┫┏━━╋┫┃┃┃━┫
# ┏┛┗┛┃┗┛┃┗━┫┏┓┫┃━┫┃┃┃╋╋┃┃┗┫┃━┫
# ┗━━━┻━━┻━━┻┛┗┻━━┻┛┗┛╋╋┗┻━┻━━┛

FROM nginx:mainline-alpine
LABEL Author="ChristianHart,DanielS1996"

RUN apk add php7 php7-fpm php7-opcache

#WORKDIR "/www"
#RUN make /app
#COPY entrypoint.sh /entrypoint.sh

#CMD ["/entrypoint.sh"]
COPY index.html /usr/share/nginx/html/index.html

EXPOSE 80
