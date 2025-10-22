# importing Flask and other modules

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
            age = int(request.form.get("age"))  # getting input with name = age in HTML form
            sex = int(request.form.get("sex"))  # getting input with name = sex in HTML form
            cp = int(request.form.get("cp"))
            trestbps = int(request.form.get("trestbps"))
            chol = int(request.form.get("chol"))
            fbs = int(request.form.get("fbs"))
            restecg = int(request.form.get("restecg"))
            thalach = int(request.form.get("thalach"))
            exang = int(request.form.get("exang"))
            oldpeak = float(request.form.get("oldpeak"))
            slope = int(request.form.get("slope"))
            ca = int(request.form.get("ca"))
            thal = int(request.form.get("thal"))
        except (ValueError, TypeError) as e:
            return jsonify(message="Invalid input: Please fill all fields with valid numbers"), 400

        # we will replace this simple (and inaccurate logic) with a prediction from a machine learning model in a
        # future lab
        # Simple risk assessment based on multiple factors
        if (age > 60 and chol > 240) or (cp == 3 and thalach < 120):
            prediction_value = True
        else:
            prediction_value = False

        return render_template("response_page.html",
                               prediction_variable=prediction_value)

    else:
        return jsonify(message="Method Not Allowed"), 405  # The 405 Method Not Allowed should be used to indicate
    # that our app that does not allow the users to perform any other HTTP method (e.g., PUT and  DELETE) for
    # '/checkheart' path


# The code within this conditional block will only run the python file is executed as a
# script. See https://realpython.com/if-name-main-python/
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001)
