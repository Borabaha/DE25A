# Training API - XGBoost Version

Alternative implementation of the Heart Disease prediction training API using **XGBoost** instead of Neural Networks.

## 🎯 Overview

This is a **bonus/alternative** implementation to demonstrate model comparison. The main implementation (Lab2-compliant) uses Neural Networks with Keras.

## 🔄 Key Differences from Neural Network Version

### Model Type
- **Neural Network:** Sequential model with Dense layers (24-16-8-1)
- **XGBoost:** Gradient Boosting with 100 decision trees

### Performance
| Metric | Neural Network | XGBoost |
|--------|---------------|---------|
| Training Time | ~30-60 seconds | ~2-5 seconds |
| Accuracy | ~0.82-0.86 | ~0.85-0.90 |
| Docker Image | ~2 GB | ~500 MB |
| Dependencies | TensorFlow, Keras | XGBoost, scikit-learn |

### Output Metrics
XGBoost provides more comprehensive metrics:
- Accuracy
- Precision
- Recall
- F1-score
- Model type information

### File Format
- **Neural Network:** `model.keras` (HDF5-based, ~1-5 MB)
- **XGBoost:** `model.pkl` (Pickle, ~500 KB)

## 🚀 Usage

### Local Development

1. **Install dependencies:**
```bash
pip install -r requirements.txt
```

2. **Run the Flask app:**
```bash
python app.py
```

3. **Send training request:**
```bash
curl -X POST http://localhost:5000/training-api/model \
  -H "Content-Type: application/json" \
  -d @train_data.json
```

### Docker

1. **Build the image:**
```bash
docker build -t heart-disease-training-xgboost .
```

2. **Run the container:**
```bash
docker run -p 5000:5000 heart-disease-training-xgboost
```

3. **Test the API:**
```bash
curl -X POST http://localhost:5000/training-api/model \
  -H "Content-Type: application/json" \
  -d @train_data.json
```

## 📊 Expected Response

```json
{
  "accuracy": 0.8881578947368421,
  "precision": 0.9047619047619048,
  "recall": 0.8636363636363636,
  "f1_score": 0.8837209302325582,
  "model_type": "XGBoost",
  "n_estimators": 100,
  "max_depth": 5
}
```

## 🔧 Model Parameters

- **n_estimators:** 100 (number of boosting rounds)
- **max_depth:** 5 (maximum tree depth)
- **learning_rate:** 0.1 (step size shrinkage)
- **random_state:** 42 (for reproducibility)
- **eval_metric:** logloss

## 📁 Project Structure

```
training-api-xgboost/
├── app.py                      # Flask application (same as NN version)
├── resources/
│   ├── __init__.py
│   └── model_trainer.py        # XGBoost implementation
├── requirements.txt            # Dependencies (lighter than NN)
├── Dockerfile                  # Docker configuration
├── .dockerignore
├── train_data.json            # Training data (304 samples)
└── README.md                   # This file
```

## 🎓 Why XGBoost?

### Advantages:
- ✅ **Faster training** (5-10x faster than Neural Networks)
- ✅ **Better performance** on tabular data
- ✅ **Less overfitting** (built-in regularization)
- ✅ **Feature importance** (interpretable)
- ✅ **Lighter dependencies** (no TensorFlow needed)
- ✅ **Smaller Docker image** (4x smaller)

### Disadvantages:
- ❌ Not Lab2-compliant (Lab2 requires Keras)
- ❌ Different file format (.pkl vs .keras)
- ❌ Different API for predictions

## 📝 Notes

- This is an **alternative/bonus** implementation
- The main implementation in `training-api/` follows Lab2 requirements
- Both implementations use the same Flask API structure
- Both accept the same JSON training data format
- Model files are saved in different formats

## 🔗 API Endpoint

```
POST /training-api/model
```

**Request:** JSON array with 13 features + 1 target
**Response:** JSON with accuracy, precision, recall, f1_score

---

**Author:** Data Engineering Assignment - Part 1 (Bonus)
**Dataset:** Heart Disease Cleveland (304 samples, 13 features)

