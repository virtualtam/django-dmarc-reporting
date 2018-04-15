FROM alpine:3.7
LABEL maintainer="VirtualTam"

RUN apk --update --no-cache add \
    ca-certificates \
    nginx \
    python3 \
    s6 \
    sqlite

ADD deploy/nginx.conf /etc/nginx/nginx.conf
ADD deploy/services.d /etc/services.d

ADD . /app
WORKDIR /app
RUN pip3 install -r deploy/requirements.txt

RUN adduser -D -h /var/lib/app app
RUN chown -R app:app /app

EXPOSE 80

CMD ["/app/deploy/entrypoint.sh"]
