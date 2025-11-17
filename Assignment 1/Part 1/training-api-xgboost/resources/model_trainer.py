# XGBoost for Heart Disease Cleveland Dataset
# Alternative implementation to Neural Network approach
import logging
import os
import pickle

from flask import jsonify
from xgboost import XGBClassifier
import numpy as np


def train(dataset):
    # split into input (X) and output (Y) variables
    # Heart Disease has 13 features (columns 0-12) and 1 target (column 13)
    X = dataset[:, 0:13]
    Y = dataset[:, 13]
    
    # Define XGBoost model with optimized parameters
    model = XGBClassifier(
        n_estimators=100,           # Number of boosting rounds
        max_depth=5,                # Maximum tree depth
        learning_rate=0.1,          # Step size shrinkage
        random_state=42,            # For reproducibility
        eval_metric='logloss',      # Evaluation metric
        use_label_encoder=False     # Suppress warning
    )
    
    # Fit the model
    model.fit(X, Y)
    
    # Evaluate the model
    accuracy = model.score(X, Y)
    y_pred = model.predict(X)
    
    # Calculate additional metrics
    from sklearn.metrics import precision_score, recall_score, f1_score
    precision = precision_score(Y, y_pred, zero_division=0)
    recall = recall_score(Y, y_pred, zero_division=0)
    f1 = f1_score(Y, y_pred, zero_division=0)
    
    text_out = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "model_type": "XGBoost",
        "n_estimators": 100,
        "max_depth": 5
    }
    logging.info(text_out)
    
    # Saving model in a given location provided as an env. variable
    model_repo = os.getenv('MODEL_REPO')
    if model_repo:
        os.makedirs(model_repo, exist_ok=True)
        file_path = os.path.join(model_repo, "model.pkl")
        with open(file_path, 'wb') as f:
            pickle.dump(model, f)
        logging.info("Saved the XGBoost model to the location : " + model_repo)
        return jsonify(text_out), 200
    else:
        with open("model.pkl", 'wb') as f:
            pickle.dump(model, f)
        return jsonify({'message': 'The XGBoost model was saved locally.'}), 200

