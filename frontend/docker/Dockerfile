FROM node:20-alpine AS build
WORKDIR /src
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine

RUN adduser -D bkyz-ui -H -s /sbin/nologin -u 65532 bkyz-ui

COPY docker/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build --chown=bkyz-ui:bkyz-ui /src/dist /usr/share/nginx/html

USER bkyz-ui:bkyz-ui
EXPOSE 8080
