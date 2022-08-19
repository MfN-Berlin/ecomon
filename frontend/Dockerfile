FROM node:latest AS build
WORKDIR /build

COPY package.json package.json
COPY package-lock.json package-lock.json
RUN npm ci

COPY public/ public
COPY src/ src
COPY tsconfig.json/ tsconfig.json
ENV NODE_ENV production
RUN npm run build

FROM nginx:alpine
COPY docker-build/default.conf /etc/nginx/conf.d/default.conf
COPY --from=build /build/build/ /usr/share/nginx/html