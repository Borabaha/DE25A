# importing Flask and other modules
import json
import os
import logging
import requests
from flask import Flask, request, render_template, jsonify

# Flask constructor
app = Flask(__name__)


# A decorator used to tell the application
# which URL is associated function
@app.route('/checkheart', methods=["GET", "POST"])
def check_heart():
    if request.method == "GET":
        return render_template("input_form_page.html")

    elif request.method == "POST":
        try:
            data = {
                "age": int(request.form.get("age")),
                "sex": int(request.form.get("sex")),
                "cp": int(request.form.get("cp")),
                "trestbps": int(request.form.get("trestbps")),
                "chol": int(request.form.get("chol")),
                "fbs": int(request.form.get("fbs")),
                "restecg": int(request.form.get("restecg")),
                "thalach": int(request.form.get("thalach")),
                "exang": int(request.form.get("exang")),
                "oldpeak": float(request.form.get("oldpeak")),
                "slope": int(request.form.get("slope")),
                "ca": int(request.form.get("ca")),
                "thal": int(request.form.get("thal")),
            }
            prediction_input = [data]
        except (ValueError, TypeError) as e:
            app.logger.warning("Invalid input parse error: %s", e)
            return jsonify(message=f"Invalid input: {str(e)}. Ensure all fields are numeric (use '.' for decimals)."), 400

        app.logger.debug("Prediction input : %s", prediction_input)

        # use requests library to execute the prediction service API by sending an HTTP POST request
        # use an environment variable to find the value of the heart disease prediction API
        # json.dumps() function will convert a subset of Python objects into a json string.
        # json.loads() method can be used to parse a valid JSON string and convert it into a Python Dictionary.
        predictor_api_url = os.environ.get('PREDICTOR_API', 'NOT_SET')
        app.logger.info("Calling API: %s", predictor_api_url)
        if not predictor_api_url or predictor_api_url == 'NOT_SET':
            app.logger.error("PREDICTOR_API environment variable is not set")
            return jsonify(message="Prediction service is not configured (PREDICTOR_API missing)."), 500
        
        try:
            res = requests.post(predictor_api_url, json=json.loads(json.dumps(prediction_input)), timeout=30)
            app.logger.info("API Response Status: %s", res.status_code)
            app.logger.info("API Response Text: %s", res.text)
            
            if res.status_code != 200:
                return jsonify(message=f"API Error: Status {res.status_code}, Response: {res.text}"), res.status_code

            try:
                prediction_value = res.json()['result']
            except Exception as e:
                app.logger.error("Failed to decode JSON or missing 'result': %s; body: %s", e, res.text)
                return jsonify(message="Error processing prediction response from service"), 500
            app.logger.info("Prediction Output : %s", prediction_value)
            return render_template("response_page.html",
                                   prediction_variable=eval(prediction_value))
        except requests.exceptions.RequestException as e:
            app.logger.error("Request failed: %s", str(e))
            return jsonify(message=f"Failed to call prediction API: {str(e)}"), 500
        except (KeyError, ValueError) as e:
            app.logger.error("Invalid response: %s", str(e))
            return jsonify(message=f"Invalid response from API: {str(e)}, Response: {res.text}"), 500

    else:
        return jsonify(message="Method Not Allowed"), 405  # The 405 Method Not Allowed should be used to indicate
    # that our app that does not allow the users to perform any other HTTP method (e.g., PUT and  DELETE) for
    # '/checkheart' path


# The code within this conditional block will only run the python file is executed as a
# script. See https://realpython.com/if-name-main-python/
if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)), host='0.0.0.0', debug=True)
