
# # Part2

# In[1]:


import requests
import gzip
import os
import tensorflow as tf
#from sklearn.model_selection import train_test_split
from tensorflow.python.tools import inspect_checkpoint as chkp
from tensorflow import keras
import numpy as np
import matplotlib.pyplot as plt


# In[2]:


#provided function
def get_testset():
    url = 'https://courses.engr.illinois.edu/ece498icc/sp2019/lab2_request_dataset.php'
    values = {'request': 'testdata', 'netid':'smeng10'}
    r = requests.post(url, data=values, allow_redirects=True)
    filename = r.url.split("/")[-1]
    testset_id = filename.split(".")[0].split("_")[-1]
    with open(filename, 'wb') as f: 
        f.write(r.content)
    return load_dataset(filename), testset_id

def load_dataset(path):
    num_img = 1000
    with gzip.open(path, 'rb') as infile:
        data = np.frombuffer(infile.read(), dtype=np.uint8).reshape(num_img, 784)
    return data

def send_result(pred, testset_id):
    url = 'https://courses.engr.illinois.edu/ece498icc/sp2019/lab2_request_dataset.php'
    values = {'request': 'verify', 'netid':'smeng10', 'testset_id' : testset_id, 'prediction' : pred}
    r = requests.post(url, data=values, allow_redirects=True)
    return r


# In[3]:


#module setup
fashion_mnist = keras.datasets.fashion_mnist
(train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()
train_images = train_images.reshape((train_images.shape[0], 28, 28, 1))
test_images = test_images.reshape((test_images.shape[0], 28, 28, 1))

class_names = ['T-shirt/top', 'Trouser', 'Pullover', 'Dress', 'Coat', 
               'Sandal', 'Shirt', 'Sneaker', 'Bag', 'Ankle boot']

train_images = train_images / 255.0
test_images = test_images / 225.0

#KERAS module
def create_keras_model():
    model = tf.keras.Sequential()
    model.add(tf.keras.layers.Conv2D(filters=3, kernel_size=5, padding='valid', activation='relu', input_shape=(28,28,1))) 
    model.add(tf.keras.layers.MaxPooling2D(strides=2))
    model.add(tf.keras.layers.Conv2D(filters=3, kernel_size=3, padding='same', activation='relu'))
    model.add(tf.keras.layers.MaxPooling2D(strides=2))
    model.add(tf.keras.layers.Flatten())
    model.add(tf.keras.layers.Dense(100, activation='relu'))
    model.add(tf.keras.layers.Dense(50, activation='relu'))
    model.add(tf.keras.layers.Dense(10, activation='softmax'))
    
    model.compile(optimizer='adam', 
              loss='sparse_categorical_crossentropy',
              metrics=['accuracy'])

    model.summary()
    return model


#TF module 
def conv2d(x, f, kernel, padding = 'valid'):
    # Conv2D wrapper, with bias and relu activation
    x = tf.layers.conv2d(inputs = x, filters = f, kernel_size = kernel, strides=1, padding=padding, activation='relu')
    return x

def maxpool2d(x):
    # MaxPool2D wrapper
    return tf.layers.max_pooling2d(x, pool_size=2, strides=2)

def conv_net(features, labels, mode):
    # MNIST data input is a 1-D vector of 784 features (28*28 pixels)
    # Reshape to match picture format [Height x Width x Channel]
    # Tensor input become 4-D: [Batch Size, Height, Width, Channel]
    x = tf.reshape(features["x"], shape=[-1, 28, 28, 1])

    # Convolution Layer 5x5 filter, stride = 1, no padding
    
    conv1 = conv2d(x, f=3, kernel=5)
    # Max Pooling (down-sampling)
    conv1 = maxpool2d(conv1)

    # Convolution Layer 3x3 filter, stride = 1, with padding
    conv2 = conv2d(conv1, f=3, kernel=3)
    # Max Pooling (down-sampling)
    conv2 = maxpool2d(conv2)

    #Flatten
    flat = tf.layers.flatten(conv2)
    # Fully connected layer
    # Reshape conv2 output to fit fully connected layer input
    # input size 108, output size 100
    fc1 = tf.layers.dense(flat, units=100, activation=tf.nn.relu)

    fc2 = tf.layers.dense(fc1, units=50, activation=tf.nn.relu)
    
    # Output, class prediction
    logits = tf.layers.dense(fc2, units=10)
    
    predictions = {
      # Generate predictions (for PREDICT and EVAL mode)
      "classes": tf.argmax(input=logits, axis=1),
      # Add `softmax_tensor` to the graph. It is used for PREDICT and by the
      # `logging_hook`.
      "probabilities": tf.nn.softmax(logits, name="softmax_tensor")
    }
    
    if mode == tf.estimator.ModeKeys.PREDICT:
        return tf.estimator.EstimatorSpec(mode=mode, predictions=predictions)
    
    loss = tf.losses.sparse_softmax_cross_entropy(labels=labels, logits=logits)
    
    if mode == tf.estimator.ModeKeys.TRAIN:
        optimizer = tf.train.GradientDescentOptimizer(learning_rate=0.001)
        train_op = optimizer.minimize(
            loss=loss,
            global_step=tf.train.get_global_step())
        return tf.estimator.EstimatorSpec(mode=tf.estimator.ModeKeys.TRAIN, loss=loss, train_op=train_op)

    eval_metric_ops = {
      "accuracy": tf.metrics.accuracy(
          labels=labels, predictions=predictions["classes"])
      }
    return tf.estimator.EstimatorSpec(
      mode=mode, loss=loss, eval_metric_ops=eval_metric_ops)
    


# In[6]:


def part2_test(test_img, mode):
    #KERAS checkpoint
    checkpoint_path = "k/"
    checkpoint_dir = os.path.dirname(checkpoint_path)
    cp_callback = tf.keras.callbacks.ModelCheckpoint(checkpoint_path, 
                                                 save_weights_only=True,
                                                 verbose=1)
    
    #TF checkpoint
    tf_cp = "fashion_classifier/"
    
    if (mode == 'keras'):
        model = create_keras_model()
        model.load_weights(checkpoint_path)
        pred = model.predict(test_img)
        pred = ''.join(list(map(lambda x: str(x.argmax()),pred)))
    
    if (mode == 'tf'):
        fashion_classifier = tf.estimator.Estimator(model_fn=conv_net, model_dir=tf_cp)
        eval_input_fn = tf.estimator.inputs.numpy_input_fn(
            x={"x": test_img},
            num_epochs=1,
            shuffle=False)
        pred = fashion_classifier.predict(input_fn=eval_input_fn)
        pred = "".join(list(map(lambda x: str(x['classes']),pred)))
    return pred

def autotestall():
    data = get_testset()
    imgs = data[0].reshape((data[0].shape[0], 28, 28, 1))/255.0
    #test keras
    predic = part2_test(imgs,'keras')
    r = send_result(pred=predic, testset_id=data[1])
    print 'keras accuracy is '+ r.text
    
    #test tf
    predic = part2_test(imgs,'tf')
    r = send_result(pred=predic, testset_id=data[1])
    print 'tensorflow accuracy is '+r.text


# In[10]:


autotestall()

