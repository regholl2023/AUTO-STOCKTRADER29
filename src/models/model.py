import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow.python.keras.models import Sequential, load_model
from tensorflow.python.keras.layers import *
from sklearn.preprocessing import MinMaxScaler

def create_dataset(dataset, look_back=1):
    X, Y = [], []
    for i in range(len(dataset)-look_back-1):
        a = dataset[i:(i+look_back), 0]
        X.append(a)
        Y.append(dataset[i + look_back, 0])
    return np.array(X), np.array(Y)

def train_lstm(data, look_back=1):
    scaler = MinMaxScaler(feature_range=(0, 1))
    dataset = scaler.fit_transform(data['Adj Close'].values.reshape(-1, 1))
    
    train_size = int(len(dataset) * 0.67)
    train, test = dataset[0:train_size, :], dataset[train_size:len(dataset), :]
    
    X_train, Y_train = create_dataset(train, look_back)
    X_test, Y_test = create_dataset(test, look_back)
    
    X_train = np.reshape(X_train, (X_train.shape[0, 1, X_train.shape[1]]))
    X_test = np.reshape(X_test, (X_test.shape[0, 1, X_test.shape[1]]))
    
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(1, look_back)))
    model.add(Dropout(0.2))
    model.add(LSTM(50, return_sequences=False))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(loss='mean_squared_error', optimizer='adam')
    
    model.fit(X_train, Y_train, epochs=100, batch_size=64, validation_data=(X_test, Y_test), verbose=1, shuffle=False)
    
    train_predict = model.predict(X_train)
    test_predict = model.predict(X_test)
    
    train_predict = scaler.inverse_transform(train_predict)
    test_predict = scaler.inverse_transform(test_predict)
    
    return model, scaler, train_predict, test_predict
