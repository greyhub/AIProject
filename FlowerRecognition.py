import os
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, precision_score, recall_score, confusion_matrix, roc_curve, roc_auc_score
from sklearn.model_selection import GridSearchCV
from sklearn.preprocessing import LabelEncoder
from keras.preprocessing.image import ImageDataGenerator
from keras import backend as K
from keras.models import Sequential
from keras.layers import Dense
from keras.optimizers import Adam, SGD, Adagrad, Adadelta, RMSprop
from keras.utils import to_categorical
from keras.layers import Dropout, Flatten, Activation
from keras.layers import Conv2D, MaxPooling2D, BatchNormalization
import tensorflow as tf
import random as rn
import cv2
import numpy as np
from tqdm import tqdm
from random import shuffle
from zipfile import ZipFile
from PIL import Image
from keras.callbacks import ReduceLROnPlateau


print(os.listdir('../flowers'))

warnings.filterwarnings('always')
warnings.filterwarnings('ignore')

#%matplotlib inline
#style.use('dark_background')
#sns.set(style='darkgrid', color_codes='d')
X = []
Z = []
IMG_SIZE = 150
FLOWER_DAISY_DIR = '../flowers/daisy'
FLOWER_SUNFLOWER_DIR = '../flowers/sunflower'
FLOWER_TULIP_DIR = '../flowers/tulip'
FLOWER_DANDI_DIR = '../flowers/dandelion'
FLOWER_ROSE_DIR = '../flowers/rose'


def assign_label(img, flower_type):
    return flower_type


def make_train_data(flower_type, DIR):
    for img in tqdm(os.listdir(DIR)):
        label = assign_label(img, flower_type)
        path = os.path.join(DIR, img)
        img = cv2.imread(path, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (IMG_SIZE, IMG_SIZE))
        X.append(np.array(img))
        Z.append(str(label))


make_train_data('Daisy', FLOWER_DAISY_DIR)
print(len(X))

make_train_data('Sunflower', FLOWER_SUNFLOWER_DIR)
print(len(X))

make_train_data('Tulip', FLOWER_TULIP_DIR)
print(len(X))

make_train_data('Rose', FLOWER_ROSE_DIR)
print(len(X))

make_train_data('Dandelion', FLOWER_DANDI_DIR)
print(len(X))

fig, ax = plt.subplots(4, 3)
fig.set_size_inches(15, 15)
for i in range(4):
    for j in range(3):
        l = rn.randint(0, len(Z))
        ax[i, j].imshow(X[l])
        ax[i, j].set_title('Flower: ' + Z[l])

plt.tight_layout()

le = LabelEncoder()
Y = le.fit_transform(Z)
Y = to_categorical(Y, 5)
X = np.array(X)
X = X / 255

print(Y)

x_train, x_test, y_train, y_test = train_test_split(
    X, Y,
    test_size=0.25,
    random_state=42)


np.random.seed(42)
rn.seed(42)
tf.set_random_seed(42)


print(rn.random())


model = Sequential()
model.add(Conv2D(filters=32, kernel_size=(5, 5), padding='Same', activation='relu', input_shape=(150, 150, 3)))
model.add(MaxPooling2D(pool_size=(2, 2)))


model.add(Conv2D(filters=64, kernel_size=(3, 3), padding='Same', activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))


model.add(Conv2D(filters=96, kernel_size=(3, 3), padding='Same', activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

model.add(Conv2D(filters=96, kernel_size=(3, 3), padding='Same', activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2), strides=(2, 2)))

model.add(Flatten())
model.add(Dense(512))
model.add(Activation('relu'))
model.add(Dense(5, activation="softmax"))


batch_size = 128
epochs = 50

red_lr = ReduceLROnPlateau(monitor='val_acc', patience=3, verbose=1, factor=0.1)


datagen = ImageDataGenerator(
        featurewise_center=False,
        samplewise_center=False,
        featurewise_std_normalization=False,
        samplewise_std_normalization=False,
        zca_whitening=False,
        rotation_range=10,
        zoom_range=0.1,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        vertical_flip=False)


datagen.fit(x_train)


model.compile(optimizer=Adam(lr=0.001), loss='categorical_crossentropy', metrics=['accuracy'])


model.summary()


History = model.fit_generator(datagen.flow(x_train,y_train, batch_size=batch_size),
                              epochs=epochs, validation_data=(x_test, y_test),
                              verbose=1, steps_per_epoch=x_train.shape[0] // batch_size)


plt.plot(History.history['loss'])
plt.plot(History.history['val_loss'])
plt.title('Model Loss')
plt.ylabel('Loss')
plt.xlabel('Epochs')
plt.legend(['train', 'test'])
plt.show()


plt.plot(History.history['acc'])
plt.plot(History.history['val_acc'])
plt.title('Model Accuracy')
plt.ylabel('Accuracy')
plt.xlabel('Epochs')
plt.legend(['train', 'test'])
plt.show()


pred = model.predict(x_test)
pred_digits = np.argmax(pred, axis=1)


i = 0
prop_class = []
mis_class = []

for i in range(len(y_test)):
    if(np.argmax(y_test[i]) == pred_digits[i]):
        prop_class.append(i)
    if(len(prop_class) == 8):
        break

i = 0
for i in range(len(y_test)):
    if(not np.argmax(y_test[i]) == pred_digits[i]):
        mis_class.append(i)
    if(len(mis_class) == 8):
        break


warnings.filterwarnings('always')
warnings.filterwarnings('ignore')

count = 0
fig, ax = plt.subplots(4, 2)
fig.set_size_inches(15, 15)
for i in range(4):
    for j in range(2):
        ax[i, j].imshow(x_test[prop_class[count]])
        ax[i, j].set_title(
            "Predicted Flower : " +
            str(le.inverse_transform([pred_digits[prop_class[count]]])) +
            "\n" +
            "Actual Flower : " +
            str(le.inverse_transform(np.argmax([y_test[prop_class[count]]]))))
        plt.tight_layout()
        count += 1


warnings.filterwarnings('always')
warnings.filterwarnings('ignore')

count = 0
fig, ax = plt.subplots(4, 2)
fig.set_size_inches(15, 15)
for i in range(4):
    for j in range(2):
        ax[i, j].imshow(x_test[mis_class[count]])
        ax[i, j].set_title(
            "Predicted Flower : " +
            str(le.inverse_transform([pred_digits[mis_class[count]]])) +
            "\n" +
            "Actual Flower : " +
            str(le.inverse_transform(np.argmax([y_test[mis_class[count]]]))))
        plt.tight_layout()
        count += 1
