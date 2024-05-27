from keras.models import Sequential
from keras.layers import Conv2D
from keras.layers import Flatten, Dense, BatchNormalization
from keras.callbacks import ModelCheckpoint, EarlyStopping
from timeit import timeit
from keras_preprocessing.image import ImageDataGenerator

ih = 468
iw = 468

def get_model():
    model = Sequential()

    # CNN 1
    model.add(Conv2D(32, kernel_size=3, strides=3, activation='relu', input_shape=(ih, iw, 3)))
    model.add(BatchNormalization())

    model.add(Flatten())

    # Connected 1
    model.add(Dense(64, activation='relu'))
    model.add(BatchNormalization())

    # Final
    model.add(Dense(3, activation='softmax'))

    model.compile(
              loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

    return model

@timeit
def train():
    callbacks = [EarlyStopping(patience=5), ModelCheckpoint(filepath='maps.h5', save_best_only=True)]

    bs = 64
    vs = 0.2

    model = get_model()

    idg = ImageDataGenerator(validation_split=vs)

    gen_train = idg.flow_from_directory(
        directory='../data/maps',
        class_mode='categorical',
        subset='training',
        batch_size=bs,
        target_size=(ih, iw))

    gen_valid = idg.flow_from_directory(
        directory='../data/maps',
        class_mode='categorical',
        subset='validation',
        batch_size=bs,
        target_size=(ih, iw))

    model.fit_generator(gen_train,
         validation_data=gen_valid,
         callbacks=callbacks,
         steps_per_epoch=100,
         validation_steps=20,
         epochs=19)

    exit()

train()

print("DONE!")