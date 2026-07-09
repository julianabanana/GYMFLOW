# GymFlow frontend — React + Vite + Tailwind
# Build multi-stage: compila con Node, sirve el resultado estático con nginx
# (nginx, no "vite preview", porque preview no está pensado para producción).

FROM node:20-slim AS build
WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:1.27-alpine AS runtime
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
