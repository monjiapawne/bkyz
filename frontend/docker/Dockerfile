FROM node:20-alpine AS build
WORKDIR /src
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build --chown=bkyz-ui:bkyz-ui /src/dist /usr/share/nginx/html

RUN adduser -D bkyz-ui -H -s /sbin/nologin -u 101 bkyz-ui
USER bkyz-ui:bkyz-ui
EXPOSE 8080
