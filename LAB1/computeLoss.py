import tensorflow as tf
import numpy as np

def function(session, loss):
	p_loss = session.run(loss)
	return p_loss
	
