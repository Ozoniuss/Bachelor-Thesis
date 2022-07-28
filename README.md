# Goal

The final goal of this project would be to enable easily creating, storing and configuring machine learning classification models based on neural networks, training them on advanced cloud hardware and benchmarking them agains other models. 

In particular, this use case is related to transfer learning. It would be desired to easily use existing feature vectors that were trained while performing a classification task, and then add a new output layer and a dataset for a new classification task, train the new model in the cloud and then benchmark it against other models. This would make it very convenient to experiment with different configurations and parameters for performing a classification task, as well as comparing the new model with other models for that classification task.

The following features are proposed:

- Downloading/Uploading certain machine learning models and feature vectors
- Adding a new output layer to a feature vector to perform a different task, either via uploading some configuration or making the configuration directly in the U.I.
- Attaching a dataset to train a model, given that the dataset is compatible with the input of the model
- Training the new model obtained from the feature vector and the new output layer on the cloud with the provided dataset
- Benchmarking a model on some dataset and displaying those benchmarks
- Comparing the performance of two models on the same task (possibly by displaying some graphs)
- Storing the created and downloaded/uploaded models
- Viewing a list of created or downloaded/uploaded models (and possibly a list of the datasets they were trained on as well as their benchmarks on those datasets)

This is only a high-level overview of the list of features, I might update it in the future. Basically, it shall be simple to attach a new head to an existing model, train it to perform a new task, benchmark it and download it.

