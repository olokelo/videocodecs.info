FROM nginx:mainline-alpine

COPY ./docker/nginx.conf /etc/nginx/nginx.conf
COPY ./vivict/build /www/vivict
COPY ./frontend /www/frontend
