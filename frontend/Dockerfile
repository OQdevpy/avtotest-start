FROM node:22-alpine AS build
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --no-audit --no-fund
COPY . .
RUN npm run build

FROM nginx:1.27-alpine
ARG ADMIN_URL=boshqaruv-7f3a/
COPY nginx.conf /etc/nginx/templates/default.conf.template
ENV ADMIN_URL=${ADMIN_URL}
ENV NGINX_ENVSUBST_FILTER=ADMIN_URL
COPY --from=build /app/dist /srv/www
