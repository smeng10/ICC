import tensorflow as tf
import numpy as np
def function(shape):
	retval = tf.Variable(initial_value=np.random.random(shape), dtype=tf.float32);
	return retval
