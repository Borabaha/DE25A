import argparse
import logging
import sys
from pathlib import Path
from flask import Flask, jsonify

from google.cloud import storage


def download_data(project_id, bucket, file_name, feature_path):
    logging.basicConfig(stream=sys.stdout, level=logging.INFO)
    client = storage.Client(project=project_id)
    bucket = client.get_bucket(bucket)
    blob = bucket.blob(file_name)
    # Creating the directory where the output file is created (the directory
    # may or may not exist).
    Path(feature_path).parent.mkdir(parents=True, exist_ok=True)
    blob.download_to_filename(feature_path)
    logging.info('Downloaded Data!')

app = Flask(__name__)

@app.route("/run", methods=["POST"])
def run_component():
    print("Running data ingestion...")

    download_data(
        project_id="de2025-475823",
        bucket="data_de2025_group6",
        file_name="Heart_disease_cleveland_new.csv",
        feature_path="/tmp/Heart_disease_cleveland_new.csv"
    )

    return jsonify({"status": "success", "message": "Data ingestion completed!"})

if __name__ == "__main__":
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)