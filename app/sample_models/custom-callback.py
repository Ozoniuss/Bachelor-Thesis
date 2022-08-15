from keras.callbacks import Callback


class CustomCallback(Callback):
    def on_epoch_begin(self, epoch, logs=None):
        print("prindemiai coaiele si puneleai in gura")
