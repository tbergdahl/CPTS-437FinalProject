import numpy as np
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt
import datetime
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

#Downloading Dataset form yfinance
ticker = 'AAPL'
start_date = '2012-01-01'
end_date = '2024-01-01'
data = yf.download(ticker, start=start_date, end=end_date)

#Extracting closing prices
closing_prices = data[['Close']]

#Preprocessing the data to make it more suitable for the LSTM model
scaler = MinMaxScaler(feature_range=(0,1))
scaled_data = scaler.fit_transform(closing_prices)

#Using a 60 day frame for training in order to predict the next day
days_sequence_len = 60
X_train, y_train = [], []

for i in range(days_sequence_len, len(scaled_data)):
    X_train.append(scaled_data[i-days_sequence_len:i, 0])
    y_train.append(scaled_data[i, 0])

X_train, y_train = np.array(X_train), np.array(y_train)
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

#Building the LSTM Model
model = Sequential()
model.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
model.add(Dropout(0.2))
model.add(LSTM(units=50, return_sequences=False))
model.add(Dropout(0.2))
#Setting Prediciton to one day in future
model.add(Dense(units=1))

model.compile(optimizer='adam', loss='mean_squared_error')

#Training the model
epochs = 50
batch_size = 32
history = model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, verbose=1)

#Prepping Test Data

#Fetching
test_data = yf.download(ticker, start='2024-01-02', end=datetime.datetime.now())
actual_closing_prices = test_data['Close'].values

#Scaling and setting sequence
total_data = pd.concat((data['Close'], test_data['Close']), axis=0)
test_inputs = total_data[len(total_data) - len(test_data) - days_sequence_len:].values
test_inputs = test_inputs.reshape(-1, 1)
test_inputs = scaler.transform(test_inputs)

X_test = []
for i in range(days_sequence_len, len(test_inputs)):
    X_test.append(test_inputs[i-days_sequence_len:i, 0])

X_test = np.array(X_test)
X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

#Make prediction
predicted_prices = model.predict(X_test)
predicted_prices = scaler.inverse_transform(predicted_prices)

#Plot Actual v Predicted
plt.figure(figsize=(14, 5))
plt.plot(actual_closing_prices, color="black", label="Actual Price")
plt.plot(predicted_prices, color="green", label="Predicted Price")
plt.title(f'{ticker} Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Stock Price')
plt.legend()
plt.show()