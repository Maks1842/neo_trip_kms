# ---------- Стадия сборки ----------
FROM node:22-alpine AS builder

WORKDIR /app

# Зависимости ставятся отдельным слоем: пока package-lock.json не меняется,
# слой берётся из кэша.
COPY package.json package-lock.json ./
RUN npm ci

COPY . .
RUN npm run build

# ---------- Стадия раздачи ----------
FROM nginx:alpine AS runtime

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
