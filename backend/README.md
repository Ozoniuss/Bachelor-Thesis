# Goal

-----
## Note: add maximum model size.
-- can train any model on any dataset by just changing the output layer. need to make a copy of the model and go train it
-- this means that we care about the model's input (and possibly preprocessing)
-- trainings are still stored, but again, can be done on any dataset
-- models can be evaluated on images on any list of images.
-- "type" simply means set of output labels
-- can make a model public?
-- feature vector or not? (just an if in the code)

-----

The final goal of this project would be to enable easily creating, storing and configuring machine learning classification models based on neural networks, training them on advanced cloud hardware and benchmarking them agains other models. 

In particular, this use case is related to transfer learning. It would be desired to easily use existing feature vectors that were trained while performing a classification task, and then add a new output layer and a dataset for a new classification task, train the new model in the cloud and then benchmark it against other models. This would make it very convenient to experiment with different configurations and parameters for performing a classification task, as well as comparing the new model with other models for that classification task.

For my thesis, I will be implementing a simplified version of this idea. This is mostly due to lack of time. The following features are proposed in my thesis application:

- The backbone of all models is the keras library. Each model is a keras.Sequential model instance.
- Provide a distinction between public and private models. Public models are visible to all users and are available for download, while private models are only visible to the user that created them.
- Provide a public list of datasets. It shall be impossible to make datasets private on the platform to encourage collaboration.
- It is desirable that every model could be trained on any dataset. This is supposed to fasten the process of transfer learning. By default, if the set of labels that were the output of the model is different from the set of labels of the dataset, the output layer is replaced with a fresh Dense softmax layer. If there is time left, this might be configurable. For now, it is not possible to train an entire model due to limited hardware.
- All data is pre-processed the same way: 224x224 8 bit colored images. This might also be configurable in the future.
- The user has the possibility to update the model after a training, in which case the training results get stored. This includes the dataset, the compiler used, the loss function, the number of epochs, the accuracy and loss value in each epoch. If the model is deleted, the training is also deleted. It shall also be possible to disregard the update, or to both keep the updated model and the original model.
- Datasets cannot be deleted for now. This might be updated to allowing the deletion of datasets that are not part of the model.
- Users should be able to upload datasets and trained models.
- Possibly we want to allow