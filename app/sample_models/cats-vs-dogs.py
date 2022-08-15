from keras import Sequential
from keras.layers import Conv2D, MaxPool2D, Flatten, Dense
from keras.optimizers import adam_v2
from keras.utils import image_dataset_from_directory
from keras.layers import Rescaling
from keras.losses import SparseCategoricalCrossentropy
from app.utils import generateTrainingDataset, removeTrainingDataset
from keras.models import load_model
import tensorflow as tf

physical_devices = tf.config.experimental.list_physical_devices("GPU")
tf.config.experimental.set_memory_growth(physical_devices[0], True)

model = Sequential(
    [
        Conv2D(
            filters=32,
            kernel_size=(3, 3),
            activation="relu",
            padding="same",
            input_shape=(224, 224, 3),
        ),
        MaxPool2D(pool_size=(2, 2), strides=2),
        Conv2D(filters=64, kernel_size=(3, 3), activation="relu", padding="same"),
        MaxPool2D(pool_size=(2, 2), strides=2),
        Flatten(),
        Dense(units=2, activation="softmax"),
    ]
)

model.summary()

model.compile(
    optimizer=adam_v2.Adam(learning_rate=0.0001),
    loss=SparseCategoricalCrossentropy(from_logits=True),
    metrics=["accuracy"],
)

training_path, _ = generateTrainingDataset("cats-vs-dogs", sample_size=1000)
(training_path)

## example with image_dataset_from_directory
train_ds = image_dataset_from_directory(
    directory=training_path,
    labels="inferred",
    seed=12,
    color_mode="rgb",
    batch_size=10,
    image_size=(224, 224),
    validation_split=0.2,
    subset="training",
    shuffle=True,
)

valid_ds = image_dataset_from_directory(
    directory=training_path,
    labels="inferred",
    seed=12,
    color_mode="rgb",
    batch_size=10,
    image_size=(224, 224),
    validation_split=0.2,
    subset="validation",
    shuffle=True,
)

normalization_layer = Rescaling(1.0 / 255)

train_normalized_ds = train_ds.map(lambda x, y: (normalization_layer(x), y))
valid_normalized_ds = valid_ds.map(lambda x, y: (normalization_layer(x), y))

history = model.fit(
    train_normalized_ds,
    validation_data=valid_normalized_ds,
    epochs=10,
)

history.history
model.save(
    r"C:\personal projects\Bachelor-Thesis\models\01232321-3222-2122-bb21-6a21abab1121\test.h5"
)

removeTrainingDataset(training_path)
