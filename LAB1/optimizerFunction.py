import tensorflow as tf
import numpy as np

def function(loss, lr):
	optimizer = tf.train.AdamOptimizer(lr)
	train = optimizer.minimize(loss)
	return train
