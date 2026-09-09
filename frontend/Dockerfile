FROM node:20-alpine AS build
WORKDIR /src
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS run
RUN adduser -D bkyz-ui -H -s /sbin/nologin -u 65532 bkyz-ui
RUN npm install -g serve@14
WORKDIR /bkyz-ui
COPY --from=build --chown=bkyz-ui:bkyz-ui /src/dist /bkyz-ui/dist
USER bkyz-ui:bkyz-ui
EXPOSE 8080

# Supress access log
ENV SERVE_FLAGS=-L
CMD ["sh", "-c", "exec serve -s dist -l 8080 $SERVE_FLAGS"]