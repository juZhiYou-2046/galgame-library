# 多阶段构建：前端 + 后端

# Stage 1: 构建前端
FROM node:20-alpine AS frontend-build
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

# Stage 2: 运行后端
FROM python:3.12-slim AS runtime
WORKDIR /app

# 安装 Python 依赖
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 复制后端代码
COPY app/ ./app/

# 复制前端构建产物
COPY --from=frontend-build /build/dist ./frontend/dist

# 创建数据和封面目录
RUN mkdir -p /app/data /app/covers

# 设置环境变量
ENV DATABASE_URL=sqlite:////app/data/galgame.db
ENV CORS_ORIGINS=http://localhost:8000
ENV DATA_DIR=/app/data
ENV COVERS_DIR=/app/covers

EXPOSE 8000

# 启动命令
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
