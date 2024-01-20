import jsonpickle

def save_object(data, tar):
    jp = jsonpickle.encode(data)
    f = open(tar, 'w')
    f.write(jp)
    f.close()

def load_object(tar):
    json = open(tar, 'r').read()
    json = jsonpickle.decode(json)
    return json
