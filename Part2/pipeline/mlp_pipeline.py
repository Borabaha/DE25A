import kfp
from kfp import dsl
import requests

# === Cloud Run  ===
DATA_INGESTOR_URL = "https://dataingestor-service-41144114503.us-central1.run.app/run"
MLP_TRAINER_URL = "https://mlptrainer-service-41144114503.us-central1.run.app/train"


@dsl.component(base_image="python:3.10-slim")
def call_data_ingestor():
    import requests
    import json
    print("🔹 Calling Data Ingestor Cloud Run service...")
    resp = requests.post(DATA_INGESTOR_URL)
    print(f"Response: {resp.status_code}, {resp.text}")
    if resp.status_code != 200:
        raise RuntimeError("❌ Data Ingestor service failed!")


@dsl.component(base_image="python:3.10-slim")
def call_mlp_trainer():
    import requests
    import json
    print("🔹 Calling MLP Trainer Cloud Run service...")
    resp = requests.post(MLP_TRAINER_URL)
    print(f"Response: {resp.status_code}, {resp.text}")
    if resp.status_code != 200:
        raise RuntimeError("❌ MLP Trainer service failed!")


@dsl.pipeline(
    name="heartdisease-predictor-mlp-pipeline",
    description="Pipeline using Cloud Run components for data ingestion and model training"
)
def run_pipeline():
    data_ingestor_step = call_data_ingestor()
    mlp_trainer_step = call_mlp_trainer().after(data_ingestor_step)


if __name__ == "__main__":
    from kfp import compiler
    compiler.Compiler().compile(pipeline_func=run_pipeline,
                                package_path='heartdisease_predictor_mlp_cloudrun.yaml')
    print("✅ Pipeline compiled successfully!")
