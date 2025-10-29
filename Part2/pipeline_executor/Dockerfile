FROM python:3.9-slim

# 安装依赖
RUN pip install --no-cache-dir \
    google-cloud-aiplatform==1.38.0 \
    kfp==2.4.0

# 复制执行脚本
COPY pipeline_executor.py /pipeline_executor.py

# 设置执行权限
RUN chmod +x /pipeline_executor.py

# 入口点
ENTRYPOINT ["python3", "/pipeline_executor.py"]