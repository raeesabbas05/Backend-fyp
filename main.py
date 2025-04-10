from tensorflow.keras.models import load_model
import tensorflow as tf
import numpy as np
import pickle
import pandas as pd
# import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler

# scaler = MinMaxScaler(feature_range=(0, 1))

# with open('date_data.pkl', 'rb') as file:
#     date_data = pickle.load(file)

# with open('posted_date.pkl', 'rb') as file:
#     posted_date = pickle.load(file)

# scaler.fit_transform(date_data)


# # Load the saved model
# model = load_model('lstm_date_prediction_model.h5')


# # Recompile the model with the same loss and optimizer
# model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(learning_rate=0.001))

# # Predict the next 30 days
# future_days = 30
# look_back = 30  # This should match the look_back value used during training
# last_sequence = date_data[-look_back:]  # Get the last sequence to predict the next day

# future_predictions = []
# for _ in range(future_days):
#     next_prediction = model.predict(last_sequence.reshape(1, look_back, 1))
#     future_predictions.append(next_prediction[0, 0])
#     # Update the last sequence with the new prediction
#     last_sequence = np.append(last_sequence[1:], next_prediction)

# # Invert the predictions to get actual date values
# future_predictions = np.array(future_predictions).reshape(-1, 1)
# future_predictions = scaler.inverse_transform(future_predictions)

# # Generate future dates
# last_date = posted_date.max()
# future_dates = pd.date_range(last_date, periods=future_days + 1, inclusive='right')
# print(future_dates)
# print(future_predictions)







def predict_future_dates(data_path, model_path, future_days=31):
    # Load the dataset
    data = pd.read_csv(data_path)
    
    # Select the relevant column (date)
    data = data[['posted_date']]
    
    # Convert 'posted_date' to datetime objects
    data['posted_date'] = pd.to_datetime(data['posted_date'])
    
    # Sort data by date
    data = data.sort_values('posted_date')
    
    # Create a numerical representation of the dates (days since a reference date)
    reference_date = data['posted_date'].min()
    data['days_since'] = (data['posted_date'] - reference_date).dt.days
    
    # Drop rows with NaN values in 'days_since'
    data = data.dropna(subset=['days_since'])
    
    # Use only the 'days_since' column for prediction
    date_data = data['days_since'].values.reshape(-1, 1)
    
    # Normalize date data
    scaler = MinMaxScaler(feature_range=(0, 1))
    date_data = scaler.fit_transform(date_data)
    
    # Prepare data for LSTM (create sequences)
    look_back = 30  # Number of previous days to consider
    X, Y = [], []
    for i in range(look_back, len(date_data)):
        X.append(date_data[i - look_back:i])
        Y.append(date_data[i])
    
    X = np.array(X)
    Y = np.array(Y)
    
    # Load the saved model
    model = tf.keras.models.load_model(model_path)
    
    # Recompile the model with the same loss and optimizer
    model.compile(loss='mean_squared_error', optimizer=tf.keras.optimizers.Adam(learning_rate=0.001))
    
    # Predict the next 'future_days'
    last_sequence = date_data[-look_back:]  # Get the last sequence to predict the next day
    future_predictions = []
    
    for _ in range(future_days):
        next_prediction = model.predict(last_sequence.reshape(1, look_back, 1))
        future_predictions.append(next_prediction[0, 0])
        # Update the last sequence with the new prediction
        last_sequence = np.append(last_sequence[1:], next_prediction)
    
    # Invert the predictions to get actual date values
    future_predictions = np.array(future_predictions).reshape(-1, 1)
    future_predictions = scaler.inverse_transform(future_predictions)
    
    # Generate future dates
    last_date = data['posted_date'].max()
    future_dates = pd.date_range(last_date, periods=future_days + 1, inclusive='right')
    
    # Return future dates and predictions
    return future_dates[1:], future_predictions.flatten()

if __name__ == "__main__":
    # Example usage
    data_path = 'jobs-usa-linkedin.csv'
    model_path = 'lstm_date_prediction_model.h5'
    future_dates, future_predictions = predict_future_dates(data_path, model_path)

    print(future_dates)
    print(future_predictions)

    # Plot the future predictions
    # plt.figure(figsize=(10, 6))
    # plt.plot(future_dates, future_predictions, label='Future Predictions')
    # plt.legend()
    # plt.xlabel('Date')
    # plt.ylabel('Days Since Reference Date')
    # plt.title('Future Predictions')
    # plt.show()