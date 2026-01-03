# 开发阶段
FROM node:18-alpine as development

WORKDIR /app

# 安装依赖（使用 pnpm 与 pnpm-lock）
COPY package.json pnpm-lock.yaml ./
RUN corepack enable \
    && corepack prepare pnpm@9 --activate \
    && pnpm install --frozen-lockfile

# 复制源代码
COPY . .

# 暴露端口
EXPOSE 3000

# 启动开发服务器
CMD ["pnpm", "run", "dev", "--", "--host", "0.0.0.0"]

# 构建阶段
FROM node:18-alpine as build

WORKDIR /app

# 复制依赖文件（使用 pnpm 与 pnpm-lock）
COPY package.json pnpm-lock.yaml ./
RUN corepack enable \
    && corepack prepare pnpm@9 --activate \
    && pnpm install --frozen-lockfile

# 复制源代码并构建
COPY . .
ARG VITE_API_BASE_URL
ARG VITE_WS_BASE_URL
ENV VITE_API_BASE_URL=$VITE_API_BASE_URL
ENV VITE_WS_BASE_URL=$VITE_WS_BASE_URL

RUN pnpm run build

# 生产阶段
FROM nginx:alpine as production

# 复制构建产物到nginx
COPY --from=build /app/dist /usr/share/nginx/html

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]