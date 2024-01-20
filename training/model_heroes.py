from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import Dropout, Flatten, Dense, BatchNormalization
from keras.callbacks import ModelCheckpoint, EarlyStopping
from timeit import timeit
from keras_preprocessing.image import ImageDataGenerator
from keras.optimizers import Adam

ih = 63
iw = 56

def get_model():
    model = Sequential()

    model.add(Conv2D(32, kernel_size=3, strides=1, activation='relu', input_shape=(ih, iw, 3)))
    model.add(Conv2D(64, kernel_size=3, strides=1, activation='relu', padding='same'))
    model.add(Flatten())
    model.add(Dense(32, activation='relu'))
    model.add(Dense(10, activation='softmax'))
    model.compile(
              loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

    return model

@timeit
def train():
    callbacks = [EarlyStopping(patience=5), ModelCheckpoint(filepath='agents.h5', save_best_only=True)]

    bs = 64
    vs = 0.2

    model = get_model()

    idg = ImageDataGenerator(validation_split=vs)

    gen_train = idg.flow_from_directory(
        directory='../data/agents',
        class_mode='categorical',
        subset='training',
        batch_size=bs,
        target_size=(ih, iw))

    gen_valid = idg.flow_from_directory(
        directory='../data/agents',
        class_mode='categorical',
        subset='validation',
        batch_size=bs,
        target_size=(ih, iw))

    model.fit_generator(gen_train,
         validation_data=gen_valid,
         callbacks=callbacks,
         steps_per_epoch=100,
         validation_steps=20,
         epochs=20)

    exit()

train()

print("DONE!")