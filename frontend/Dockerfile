FROM node:18 AS build
WORKDIR /frontend
COPY ./frontend .
RUN npm install
RUN npm run build

# Serve
FROM nginx:alpine
RUN rm -rf /usr/share/nginx/html/*
COPY --from=build /frontend/dist /usr/share/nginx/html