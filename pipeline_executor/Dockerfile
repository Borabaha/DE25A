FROM python:3.9-slim

RUN pip install --no-cache-dir \
    google-cloud-aiplatform \
    kfp

COPY pipeline_executor.py /pipeline_executor.py

ENTRYPOINT ["python", "/pipeline_executor.py"]