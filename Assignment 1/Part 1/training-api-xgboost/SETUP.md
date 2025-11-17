# Setup Instructions for XGBoost Training API

## 📋 Quick Setup Checklist

- [x] app.py created
- [x] resources/model_trainer.py created (XGBoost version)
- [x] requirements.txt created
- [x] Dockerfile created
- [x] .dockerignore created
- [x] README.md created
- [ ] **train_data.json needs to be copied** ⚠️

## 🔄 Copy Training Data

You need to copy `train_data.json` from the Neural Network version:

### Option 1: Manual Copy (Windows)
```powershell
cd "Assignment\Part 1"
copy "training-api\train_data.json" "training-api-xgboost\train_data.json"
```

### Option 2: Manual Copy (File Explorer)
1. Navigate to `Assignment/Part 1/training-api/`
2. Copy `train_data.json`
3. Paste into `Assignment/Part 1/training-api-xgboost/`

## ✅ Verify Setup

After copying, check that you have these files:

```
training-api-xgboost/
├── app.py                      ✅
├── resources/
│   ├── __init__.py            ✅
│   └── model_trainer.py       ✅
├── requirements.txt           ✅
├── Dockerfile                 ✅
├── .dockerignore             ✅
├── README.md                  ✅
├── SETUP.md                   ✅
└── train_data.json            ⚠️ COPY THIS!
```

## 🧪 Test After Setup

1. **Install dependencies:**
```bash
cd "Assignment/Part 1/training-api-xgboost"
pip install -r requirements.txt
```

2. **Run the app:**
```bash
python app.py
```

3. **Test training (in another terminal):**
```bash
curl -X POST http://localhost:5000/training-api/model \
  -H "Content-Type: application/json" \
  -d @train_data.json
```

Expected output:
```json
{
  "accuracy": 0.88+,
  "precision": 0.90+,
  "recall": 0.86+,
  "f1_score": 0.88+,
  "model_type": "XGBoost"
}
```

## 🐳 Docker Test

```bash
docker build -t heart-disease-xgboost .
docker run -p 5000:5000 heart-disease-xgboost
```

---

**Note:** Once you copy `train_data.json`, you're ready to go! 🚀

