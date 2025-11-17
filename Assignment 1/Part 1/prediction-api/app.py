import os

from flask import Flask, request

from heart_disease_predictor import HeartDiseasePredictor

app = Flask(__name__)
app.config["DEBUG"] = True


@app.route('/heart_predictor/', methods=['POST']) # path of the endpoint. Accept only HTTP POST request
def predict_str():
    # the prediction input data in the message body as a JSON payload
    prediction_inout = request.get_json()
    return hdp.predict_single_record(prediction_inout)


hdp = HeartDiseasePredictor()
# The code within this conditional block will only run the python file is executed as a
# script. See https://realpython.com/if-name-main-python/
if __name__ == '__main__':
    app.run(port=int(os.getenv("PORT", 5000)), host='0.0.0.0', debug=True)
