from google.cloud import aiplatform
from kfp import dsl, compiler
import requests

# === Cloud / Project Info ===
PROJECT_ID = "de2025-475823"
REGION = "us-central1"

# === Cloud Run Endpoints ===
DATA_INGESTOR_URL = "https://dataingestor-service-41144114503.us-central1.run.app/run"
MLP_TRAINER_URL = "https://mlptrainer-service-41144114503.us-central1.run.app/train"

# === Initialize Vertex AI ===
aiplatform.init(project=PROJECT_ID, location=REGION)


# === Step 1: Define components ===
@dsl.component
def trigger_data_ingestor():
    print("🚀 Triggering Data Ingestor...")
    try:
        response = requests.post(DATA_INGESTOR_URL)
        print(f"Response: {response.text}")
        return response.text
    except Exception as e:
        print(f"❌ Data Ingestor call failed: {e}")
        raise

@dsl.component
def trigger_mlp_trainer():
    print("🚀 Triggering MLP Trainer...")
    try:
        response = requests.post(MLP_TRAINER_URL)
        print(f"Response: {response.text}")
        return response.text
    except Exception as e:
        print(f"❌ MLP Trainer call failed: {e}")
        raise


# === Step 2: Define Pipeline ===
@dsl.pipeline(
    name="heart-disease-pipeline-cloudrun",
    description="Vertex pipeline calling Cloud Run services for continuous training"
)
def heart_disease_pipeline():
    data_task = trigger_data_ingestor()
    train_task = trigger_mlp_trainer().after(data_task)


# === Step 3: Compile and Run ===
if __name__ == "__main__":
    # Compile the pipeline into a YAML package
    yaml_path = "heartdisease_predictor_mlp_cloudrun.yaml"
    compiler.Compiler().compile(
        pipeline_func=heart_disease_pipeline,
        package_path=yaml_path
    )
    print(f"✅ Pipeline compiled successfully: {yaml_path}")

    # Upload and execute the pipeline on Vertex AI
    job = aiplatform.PipelineJob(
        display_name="heart_disease_pipeline_cloudrun",
        template_path=yaml_path,
        location=REGION,
    )

    print("🚀 Submitting pipeline job to Vertex AI...")
    job.run()
    print("✅ Pipeline submitted successfully. Check Vertex AI → Pipelines for execution status.")
