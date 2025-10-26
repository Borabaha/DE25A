# Heart Disease Prediction Pipeline - Part 2

## Overview
This Vertex AI pipeline trains and compares two machine learning models for heart disease prediction:
- Neural Network (Keras)
- XGBoost

The pipeline automatically selects the best performing model and uploads it to Google Cloud Storage for deployment.

## Files Structure
```
Part2/
├── heart_disease_pipeline.ipynb    # Main pipeline notebook
├── parameters.json                  # Configuration parameters
├── builder_tool/                    # (Optional) Docker configurations for components
└── README.md                        # This file
```

## Prerequisites

1. **Google Cloud Project Setup**
   - Enable Vertex AI API
   - Enable Cloud Storage API
   - Create a service account with necessary permissions

2. **Google Cloud Storage Buckets**
   You need three buckets:
   - **Data bucket**: Store training data
   - **Model bucket**: Store trained models
   - **Temp bucket**: Store pipeline artifacts

3. **Data Preparation**
   - Upload `Heart_disease_cleveland_new.csv` to your data bucket
   - Dataset should have 13 features + 1 target column:
     - Features: age, sex, cp, trestbps, chol, fbs, restecg, thalach, exang, oldpeak, slope, ca, thal
     - Target: target (0 or 1)

## Setup Instructions

### Step 1: Create Vertex AI Workbench Instance
1. Go to Vertex AI → Workbench in Google Cloud Console
2. Create a new managed notebook instance
3. Open JupyterLab

### Step 2: Upload Files
Upload these files to your Workbench instance:
- `heart_disease_pipeline.ipynb`
- `parameters.json`

### Step 3: Configure Parameters
Edit `parameters.json` with your actual values:
```json
{
  "project_id": "your-actual-project-id",
  "data_bucket": "your-data-bucket-name",
  "trainset_filename": "Heart_disease_cleveland_new.csv",
  "model_repo": "your-model-bucket-name",
  "region": "us-central1",
  "pipeline_root": "gs://your-temp-bucket-name"
}
```

### Step 4: Run the Notebook
1. Open `heart_disease_pipeline.ipynb`
2. Update the configuration cells:
   - Set `PROJECT_ID`
   - Set `REGION`
   - Set `PIPELINE_ROOT`
3. Run all cells sequentially

## Pipeline Components

### 1. Data Ingestion
- Downloads training data from GCS bucket
- Validates data format

### 2. Model Training (Parallel)
Two models are trained simultaneously:

**Neural Network:**
- Architecture: 3-layer network (16→8→1 neurons)
- Activation: ReLU and Sigmoid
- Optimizer: Adam
- Loss: Binary Crossentropy

**XGBoost:**
- Estimators: 100 trees
- Max depth: 5
- Learning rate: 0.1

### 3. Model Comparison
- Compares accuracy of both models
- Selects the best performing model

### 4. Model Upload
- Uploads the winning model to model bucket
- Saves as `model.keras` for deployment compatibility

## Output

After successful execution:
1. A compiled pipeline YAML file: `heart_disease_training_pipeline.yaml`
2. The best model uploaded to your model bucket as `model.keras`
3. Training metrics logged in Vertex AI Pipelines console

## Viewing Pipeline Runs

1. Go to Vertex AI → Pipelines in Google Cloud Console
2. You'll see your pipeline runs with:
   - Execution graph
   - Component logs
   - Metrics comparison
   - Model artifacts

## Integration with CI/CD

This pipeline can be automated using Cloud Build (covered in Lab 3):
1. Compile the pipeline in CI/CD
2. Trigger execution via Cloud Build
3. Deploy the best model to Cloud Run

## Troubleshooting

**Issue: Package installation fails**
- Solution: Restart kernel after installation cell

**Issue: Authentication error**
- Solution: Ensure service account has correct permissions
- Required roles: Vertex AI User, Storage Object Admin

**Issue: Data not found**
- Solution: Verify file name and bucket name in parameters.json
- Check file exists in GCS bucket

**Issue: Model upload fails**
- Solution: Check model bucket permissions
- Ensure bucket exists and is accessible

## Next Steps

After pipeline execution:
1. Verify model is in model bucket
2. Update prediction API to use new model
3. Set up CI/CD pipeline for automated retraining
4. Deploy prediction service to Cloud Run

## Notes

- The pipeline uses data splitting (80/20 train/test) internally
- Feature scaling (StandardScaler) is applied automatically
- Models are evaluated on held-out test set
- Pipeline caching is disabled for consistent results

## References

- Vertex AI Pipelines: https://cloud.google.com/vertex-ai/docs/pipelines
- KFP SDK v2: https://www.kubeflow.org/docs/components/pipelines/v2/
- Cleveland Heart Disease Dataset: UCI ML Repository
