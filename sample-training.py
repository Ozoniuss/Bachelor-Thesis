"""
This is just a simple test script to check that the setup is working (the imports)
are working, the GPU is detected, the model compiles and gets trained etc.
"""

import numpy as np
from random import randint
from sklearn.utils import shuffle
from sklearn.preprocessing import MinMaxScaler

train_labels = []
train_samples = []

# 2100 participants aged 13-100, 95% of the > 65 experienced side effects and
# 95% of < 65 didn't

YOUNG = "young"
OLD = "old"
SIDES = 1
NO_SIDES = 0


def generateParticipant(category, had_sides):
    if category == YOUNG:
        age = randint(13, 64)
    elif category == OLD:
        age = randint(65, 100)
    train_samples.append(age)
    train_labels.append(had_sides)


for i in range(50):
    # 5% of younger who experienced sides
    generateParticipant(YOUNG, SIDES)
    # 5% of older who didn't experienced sides
    generateParticipant(OLD, NO_SIDES)

for i in range(1000):
    # 95% of younger who didn't experienced sides
    generateParticipant(YOUNG, NO_SIDES)
    # 95% of older who did experienced sides
    generateParticipant(OLD, SIDES)

# convert to np array to pass as input to the model
train_labels = np.array(train_labels)
train_samples = np.array(train_samples)

train_labels, train_samples = shuffle(train_labels, train_samples)

# homogenize
scaler = MinMaxScaler(feature_range=(0, 1))
scaled_train_samples = scaler.fit_transform(train_samples.reshape(-1, 1))


import tensorflow as tf
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import adam_v2
from keras.metrics import sparse_categorical_crossentropy

physical_devices = tf.config.experimental.list_physical_devices("GPU")
print("GPUs:" + str(len(physical_devices)))
tf.config.experimental.set_memory_growth(physical_devices[0], True)

model = Sequential(
    [
        # first hidden layer, we do not explicitly define the input layer
        # input shape specifies the shape of the first layer
        # 16 units for the first layer is kind of random
        # Dense means fully connected layer
        Dense(units=16, input_shape=(1,), activation="relu"),
        Dense(units=32, activation="relu"),
        Dense(units=2, activation="softmax"),
    ]
)

model.summary()

model.compile(
    optimizer=adam_v2.Adam(learning_rate=0.0001),
    loss=sparse_categorical_crossentropy,
    metrics=["accuracy"],
)

model.fit(
    x=scaled_train_samples,
    y=train_labels,
    batch_size=10,
    epochs=30,
    shuffle=True,
    verbose=2,
)
