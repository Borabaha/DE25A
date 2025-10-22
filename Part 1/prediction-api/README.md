# Prediction API - Heart Disease

Flask REST API that loads a trained Keras model and provides predictions for Heart Disease.

## Overview

This API:
1. Loads a pre-trained Keras model (`model.keras`)
2. Accepts HTTP POST requests with 13 Heart Disease features
3. Returns prediction: "True" (has disease) or "False" (no disease)

## Files

```
prediction-api/
├── app.py                          # Flask application
├── heart_disease_predictor.py      # Predictor class
├── model.keras                     # Trained model (13 features)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Docker configuration
├── .dockerignore                   # Docker ignore patterns
├── test_prediction.json           # Sample test data
└── README.md                       # This file
```

## API Endpoint

### POST /heart_predictor/

Predicts heart disease presence for a single patient.

**Request:**
```json
[
  {
    "age": 63,
    "sex": 1,
    "cp": 0,
    "trestbps": 145,
    "chol": 233,
    "fbs": 1,
    "restecg": 2,
    "thalach": 150,
    "exang": 0,
    "oldpeak": 2.3,
    "slope": 2,
    "ca": 0,
    "thal": 2
  }
]
```

**Response:**
```json
{
  "result": "True"
}
```

- `"True"` = Heart disease detected (prediction > 0.5)
- `"False"` = No heart disease (prediction ≤ 0.5)

## Setup

### Prerequisites

⚠️ **IMPORTANT:** You must have a trained model first!

1. Train the model using `training-api/`:
```bash
cd "../training-api"
pip install -r requirements.txt
python app.py

# In another terminal:
curl -X POST http://localhost:5000/training-api/model \
  -H "Content-Type: application/json" \
  -d @train_data.json
```

2. Copy the trained model:
```bash
# Windows PowerShell
copy "..\training-api\models\model.keras" "model.keras"

# Linux/Mac
cp ../training-api/models/model.keras model.keras
```

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the API:**
```bash
python app.py
```

3. **Test the API:**
```bash
curl -X POST http://localhost:5000/heart_predictor/ \
  -H "Content-Type: application/json" \
  -d @test_prediction.json
```

Expected response:
```json
{
  "result": "True"
}
```

### Docker

1. **Build the image:**
```bash
docker build -t heart-disease-prediction-api .
```

2. **Run the container:**
```bash
docker run -p 5000:5000 heart-disease-prediction-api
```

3. **Test:**
```bash
curl -X POST http://localhost:5000/heart_predictor/ \
  -H "Content-Type: application/json" \
  -d @test_prediction.json
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `MODEL_REPO` | Directory containing model.keras | `/usr/src/myapp` (Docker) or current dir |
| `PORT` | Port to run Flask app | `5000` |

## Heart Disease Features (13)

| Feature | Type | Description | Range |
|---------|------|-------------|-------|
| age | int | Age in years | 20-100 |
| sex | int | Gender | 0=female, 1=male |
| cp | int | Chest pain type | 0-3 |
| trestbps | int | Resting blood pressure (mm Hg) | 80-200 |
| chol | int | Serum cholesterol (mg/dl) | 100-600 |
| fbs | int | Fasting blood sugar > 120 mg/dl | 0=false, 1=true |
| restecg | int | Resting ECG results | 0-2 |
| thalach | int | Maximum heart rate achieved | 60-220 |
| exang | int | Exercise induced angina | 0=no, 1=yes |
| oldpeak | float | ST depression | 0.0-10.0 |
| slope | int | Slope of peak exercise ST | 0-2 |
| ca | int | Number of major vessels | 0-3 |
| thal | int | Thalassemia | 0-3 |

## Model Information

- **Input Shape:** 13 features
- **Output:** Binary classification (0 or 1)
- **Architecture:** Sequential Neural Network
  - Dense(24, relu)
  - Dense(16, relu)
  - Dense(8, relu)
  - Dense(1, sigmoid)
- **Threshold:** 0.5 (prediction > 0.5 → "True")

## Integration with prediction-ui

This API is called by `prediction-ui` to make predictions:

```
User → prediction-ui (Flask) → prediction-api (this) → model.keras → prediction
```

Set environment variable in prediction-ui:
```bash
export PREDICTOR_API=http://localhost:5000/heart_predictor/
```

## Testing Examples

### Test Case 1: High Risk Patient
```json
[
  {
    "age": 70,
    "sex": 1,
    "cp": 3,
    "trestbps": 170,
    "chol": 300,
    "fbs": 1,
    "restecg": 2,
    "thalach": 100,
    "exang": 1,
    "oldpeak": 3.5,
    "slope": 2,
    "ca": 3,
    "thal": 3
  }
]
```
Expected: `{"result": "True"}`

### Test Case 2: Low Risk Patient
```json
[
  {
    "age": 35,
    "sex": 0,
    "cp": 0,
    "trestbps": 110,
    "chol": 180,
    "fbs": 0,
    "restecg": 0,
    "thalach": 180,
    "exang": 0,
    "oldpeak": 0.0,
    "slope": 0,
    "ca": 0,
    "thal": 1
  }
]
```
Expected: `{"result": "False"}`

## Differences from Lab2

| Aspect | Lab2 (Diabetes) | This (Heart Disease) |
|--------|----------------|----------------------|
| Route | `/diabetes_predictor/` | `/heart_predictor/` |
| Class | `DiabetesPredictor` | `HeartDiseasePredictor` |
| File | `diabetes_predictor.py` | `heart_disease_predictor.py` |
| Features | 8 | 13 |
| Model Input | 8 features | 13 features |

## Troubleshooting

### Error: "MODEL_REPO is undefined"
- The API will fall back to looking for `model.keras` in the current directory
- Ensure `model.keras` exists in the same folder as `app.py`

### Error: Model expects different input shape
- Your model was trained with wrong number of features
- Retrain the model using `training-api` with 13-feature data

### Error: Cannot load model
- Ensure `model.keras` is a valid Keras model file
- Check TensorFlow/Keras version compatibility

## Dependencies

```
setuptools
flask
pandas
keras
tensorflow
numpy
h5py
six
```

## Next Steps

1. ✅ Code adapted for Heart Disease
2. ⚠️ **Replace model.keras** with 13-feature trained model
3. Test locally
4. Test with prediction-ui
5. Deploy with Docker

---

**Status:** Code complete, waiting for trained model ✅
**Dataset:** Heart Disease Cleveland (13 features)
**Lab Reference:** Lab2 Prediction API (adapted)

