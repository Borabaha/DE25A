from kfp import dsl, compiler
import requests
import time

# === Cloud Run Endpoints ===
DATA_INGESTOR_URL = "https://dataingestor-service-41144114503.us-central1.run.app/run"
MLP_TRAINER_URL = "https://mlptrainer-service-41144114503.us-central1.run.app/train"


# === Step 1: Define Components (trigger Cloud Run APIs) ===
@dsl.component
def trigger_data_ingestor():
    print("🚀 Triggering Data Ingestor (Cloud Run)...")
    try:
        response = requests.post(DATA_INGESTOR_URL)
        print(f"✅ Data Ingestor Response: {response.text}")
        return response.text
    except Exception as e:
        print(f"❌ Data Ingestor call failed: {e}")
        raise


@dsl.component
def trigger_mlp_trainer():
    print("🚀 Triggering MLP Trainer (Cloud Run)...")
    try:
        response = requests.post(MLP_TRAINER_URL)
        print(f"✅ MLP Trainer Response: {response.text}")
        return response.text
    except Exception as e:
        print(f"❌ MLP Trainer call failed: {e}")
        raise


# === Step 2: Define Logical Pipeline ===
@dsl.pipeline(
    name="heart-disease-pipeline-cloudrun",
    description="Lightweight pipeline that triggers Cloud Run APIs sequentially"
)
def heart_disease_pipeline():
    data_task = trigger_data_ingestor()
    train_task = trigger_mlp_trainer().after(data_task)


# === Step 3: Compile & Run Locally (no Vertex AI) ===
if __name__ == "__main__":
    yaml_path = "heartdisease_predictor_mlp_cloudrun.yaml"

    # Compile pipeline (optional, just for record)
    compiler.Compiler().compile(
        pipeline_func=heart_disease_pipeline,
        package_path=yaml_path
    )
    print(f"✅ Pipeline compiled successfully: {yaml_path}")

    # === Run locally instead of Vertex ===
    print("🚀 Running pipeline locally (Cloud Run only, no Vertex)...")
    try:
        # Simulate pipeline step 1
        print("\n=== STEP 1: Trigger Data Ingestor ===")
        resp1 = requests.post(DATA_INGESTOR_URL)
        print("Response:", resp1.text)

        # Wait a bit between steps
        time.sleep(3)

        # Simulate pipeline step 2
        print("\n=== STEP 2: Trigger MLP Trainer ===")
        resp2 = requests.post(MLP_TRAINER_URL)
        print("Response:", resp2.text)

        print("\n✅ Cloud Run pipeline executed successfully!")
    except Exception as e:
        print(f"❌ Error during local pipeline run: {e}")
