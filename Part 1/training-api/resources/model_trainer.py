# MLP for Heart Disease Cleveland Dataset saved to single file
# Adapted from Pima Indians Diabetes example
# see https://machinelearningmastery.com/save-load-keras-deep-learning-models/
import logging
import os

from flask import jsonify
from keras.layers import Dense
from keras.models import Sequential


def train(dataset):
    # split into input (X) and output (Y) variables
    # Heart Disease has 13 features (columns 0-12) and 1 target (column 13)
    X = dataset[:, 0:13]
    Y = dataset[:, 13]
    # define model
    model = Sequential()
    model.add(Dense(24, input_dim=13, activation='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(8, activation='relu'))
    model.add(Dense(1, activation='sigmoid'))
    # compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    # Fit the model
    model.fit(X, Y, epochs=150, batch_size=10, verbose=0)
    # evaluate the model
    scores = model.evaluate(X, Y, verbose=0)
    text_out = {
        "accuracy:": scores[1],
        "loss": scores[0],
    }
    logging.info(text_out)
    # Saving model in a given location provided as an env. variable
    model_repo = os.getenv('MODEL_REPO')
    if model_repo:
        file_path = os.path.join(model_repo, "model.keras")
        model.save(file_path)
        logging.info("Saved the model to the location : " + model_repo)
        return jsonify(text_out), 200
    else:
        model.save("model.keras")
        return jsonify({'message': 'The model was saved locally.'}), 200
