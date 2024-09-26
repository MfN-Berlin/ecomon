FROM node:latest AS build
WORKDIR /build

COPY package.json package.json
COPY package-lock.json package-lock.json
RUN npm ci

COPY public/ public
COPY src/ src
COPY tsconfig.json/ tsconfig.json
COPY config-overrides.js/ config-overrides.js

ENV NODE_ENV production
RUN npm run build

FROM nginx:alpine
COPY docker-build/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /build/build/ /app

RUN chmod -R 755 /app
RUN chown -R nginx:nginx /app

EXPOSE 80
