# Run the following command to run this file on terminal:
# python3 -m ML.train_models.train_mlp

import pandas as pd
import os
import joblib
from config import DATA_FOR_ML_MODEL_TRAINING, MODEL_PATH_WHERE_MLP_MODEL_SHOULD_GET_SAVED, PATH_FOR_SAVING_MLP_SCALAR
from config import USE_PROBABILITY_THRESHOLD, PROBABILITY_THRESHOLD, RANDOM_STATE, ML_EPOCHS, ML_BATCH_SIZE
from data.prepare_data_with_scaling import prepare_data_with_scaling
from ML.evaluate_model import evaluate_model

import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping

print('Using data file as determined in the config file to train MLP model...\n')

# Load data
data = pd.read_csv(DATA_FOR_ML_MODEL_TRAINING, index_col="Date", parse_dates=True)

# Prepare data (clean + scale)
X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names = prepare_data_with_scaling(data)

print("Training class distribution:\n", pd.Series(y_train).value_counts())
print("Test class distribution:\n", pd.Series(y_test).value_counts())
print('Data prepared successfully.\n')

# Build MLP model
input_dim = X_train_scaled.shape[1]
num_classes = 3  # Buy/Hold/Sell

model = Sequential([
    Dense(64, input_dim=input_dim, activation='relu'),
    Dropout(0.3),
    Dense(32, activation='relu'),
    Dropout(0.3),
    Dense(num_classes, activation='softmax')
])

model.compile(
    optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
    loss='sparse_categorical_crossentropy',  # y labels are integer encoded
    metrics=['accuracy']
)

# Early stopping
early_stop = EarlyStopping(monitor='val_loss', patience=10, restore_best_weights=True)

# Train model
history = model.fit(
    X_train_scaled,
    y_train,
    validation_split=0.2,
    epochs=ML_EPOCHS,
    batch_size=ML_BATCH_SIZE,
    callbacks=[early_stop],
    verbose=1
)

# Predict
probs = model.predict(X_test_scaled)
if USE_PROBABILITY_THRESHOLD:
    print(f"Using probability threshold: {PROBABILITY_THRESHOLD}")
    y_pred = []
    for p in probs:
        if p[2] >= PROBABILITY_THRESHOLD:      # Buy probability check
            y_pred.append(2)
        elif p[0] >= PROBABILITY_THRESHOLD:    # Sell probability check
            y_pred.append(0)
        else:
            y_pred.append(1)                   # Otherwise Hold
else:
    y_pred = probs.argmax(axis=1)  # Pick class with max probability

# Evaluate
evaluate_model(y_test, y_pred)

# Save model + scaler
os.makedirs(os.path.dirname(MODEL_PATH_WHERE_MLP_MODEL_SHOULD_GET_SAVED), exist_ok=True)
os.makedirs(os.path.dirname(PATH_FOR_SAVING_MLP_SCALAR), exist_ok=True)
model.save(MODEL_PATH_WHERE_MLP_MODEL_SHOULD_GET_SAVED)
joblib.dump(scaler, PATH_FOR_SAVING_MLP_SCALAR)

print(f'MLP model saved successfully as:\n{MODEL_PATH_WHERE_MLP_MODEL_SHOULD_GET_SAVED}')
print('End of training\n')

'ML/saved_models/mlp_scaler.pkl'