import os
from keras.models import load_model
import maps as mps

models = dict()

for model in os.listdir('models'):
    name = model.split('.')[0]
    models[name] = load_model('models/' + model)


def predict(model, input):
    pred = models[model].predict(input)
    i = pred.argmax(axis=1)[0]
    return mps.models[model][i], pred[0][i]