import tensorflow as tf
import numpy as np

def function(a, X, b, y):
	mul1 = a*tf.matmul(X,X,transpose_a = True)
	mul2 = tf.matmul(b, X, transpose_a = True)
	Z = mul1 +mul2
	loss = tf.pow((Z-y), 2)
	return loss
