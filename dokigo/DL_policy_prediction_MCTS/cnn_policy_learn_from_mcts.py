from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Flatten, Conv2D, MaxPooling2D
import numpy as np
from dokigo.sgfio.adaptor import SGF_to_DokiGo
from dokigo.sgfio.data_generator import SupervisedLearningDataGenerator
from dokigo.encoders.base import get_encoder_by_name
from dokigo.utilities import save_nn_model

encoder_name = 'oneplane'
generator = SupervisedLearningDataGenerator(encoder_name)
sgf_data_retriever = SGF_to_DokiGo("../../selfplay_data",generator)
X, Y = sgf_data_retriever.parse_episods()

samples = X.shape[0]
size = 9
input_shape = (size, size , 1)

X = X.reshape(samples, size,size,1)
train_samples = 8000

X_train, X_test = X[:train_samples], X[train_samples:]
Y_train, Y_test = Y[:train_samples], Y[train_samples:]

model = Sequential()
model.add(Conv2D(filters=32, kernel_size=(2,2),activation='relu', padding = 'same', input_shape=input_shape))
model.add(Dropout(rate=0.3))
model.add(Conv2D(32,(2,2), activation='relu',padding = 'same'))
model.add(MaxPooling2D(pool_size=(2,2)))
model.add(Dropout(rate=0.2))
model.add(Flatten())
model.add(Dense(64, activation='relu'))
model.add(Dropout(rate=0.2))
model.add(Dense(size * size, activation='softmax'))
model.summary()

model.compile(loss='categorical_crossentropy',
              optimizer='adam',
              metrics=['accuracy'])

model.fit(X_train, Y_train,
          batch_size=32,
          epochs=200,
          verbose=1,
          validation_data=(X_test, Y_test))
score = model.evaluate(X_test, Y_test, verbose=0)
print('Test loss:', score[0])
print('Test accuracy:', score[1])

save_nn_model("mcts_r50k.h5", model, get_encoder_by_name(encoder_name,size))

