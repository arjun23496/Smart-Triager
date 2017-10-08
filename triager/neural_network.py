from keras.models import Sequential
from keras.layers import Dense, Activation

class NeuralNetwork:

	def __init__(self):
		self.model = Sequential()

		#Layer 1
		self.model.add(Dense(units=1500, input_dim=2000))
		self.model.add(Activation('relu'))
		self.model.add(Dense(units=5))
		self.model.add(Activation('relu'))

		self.model.compile(loss='categorical_crossentropy', optimizer='sgd', metrics=['accuracy'])


	def train(self, X, y, epochs=10, batch_size=32):
		self.model.fit(X, y, epochs=epochs, batch_size=batch_size)


	def predict(self, X):
		return self.model.predict(X)


	def evaluate(self, X, y, batch_size=128):
		return self.model.evaluate(X, y, batch_size=batch_size)


	def persist_model(self, path):
		self.model.save_weights(path)


	def load_weights(self, path):
		self.model.load_weights(path)