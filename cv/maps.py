import os
path = "../data"
models = dict()

for model in os.listdir(path):
    models[model] = list()
    for category in os.listdir(path+'/'+model):
        models[model].append(category)
    models[model] = sorted(models[model])
