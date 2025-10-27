import argparse
import json
import logging
import os
import sys
from pathlib import Path

import pandas as pd
from google.cloud import storage
from keras.layers import Dense
from keras.models import Sequential


def train_mlp(project_id, feature_path, model_repo, metrics_path):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)

    df = pd.read_csv(feature_path, index_col=None)

    logging.info(df.columns)

    # split into input (X) and output (Y) variables
    feature_columns = ['age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 
                   'restecg', 'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal']
    target_column = 'target'  

    X = df[feature_columns].values
    Y = df[target_column].values
    # define model
    model = Sequential()
    model.add(Dense(12, input_dim=len(feature_columns), activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    # compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # Fit the model
    model.fit(X, Y, epochs=150, batch_size=10, verbose=0)
    # evaluate the model
    scores = model.evaluate(X, Y, verbose=0)
    logging.info(model.metrics_names)
    metrics = {
        "accuracy": scores[1],
        "loss": scores[0],
    }

    # Save the model locally
    local_file = '/tmp/local_model.keras'
    model.save(local_file)
    # Save to GCS as model.keras
    client = storage.Client(project=project_id)
    bucket = client.get_bucket(model_repo)
    blob = bucket.blob('model.keras')
    # Upload the locally saved model
    blob.upload_from_filename(local_file)
    # Clean up
    os.remove(local_file)
    print("Saved the model to GCP bucket : " + model_repo)
    # Creating the directory where the output file is created (the directory
    # may or may not exist).
    Path(metrics_path).parent.mkdir(parents=True, exist_ok=True)
    with open(metrics_path, 'w') as outfile:
        json.dump(metrics, outfile)


from flask import Flask, jsonify

app = Flask(__name__)

@app.route("/train", methods=["POST"])
def run_train():
    print("Running MLP trainer...")
    
    project_id = "de2025-475823"
    data_bucket = "data_de2025_group6"
    data_file = "Heart_disease_cleveland_new.csv"
    local_data_path = "/tmp/Heart_disease_cleveland_new.csv"
    
    # download data from GCS
    print(f"Downloading data from gs://{data_bucket}/{data_file}")
    client = storage.Client(project=project_id)
    bucket = client.get_bucket(data_bucket)
    blob = bucket.blob(data_file)
    blob.download_to_filename(local_data_path)
    print(f"Data downloaded to {local_data_path}")
    
    metrics = train_mlp(
        project_id=project_id,
        feature_path=local_data_path,
        model_repo="models_de2025_group6",
        metrics_path="/tmp/metrics.json"
    )
    
    return jsonify({"status": "success", "message": "Training completed!", "metrics": metrics})


if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)