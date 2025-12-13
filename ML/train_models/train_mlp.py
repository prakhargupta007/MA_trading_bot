# Run on terminal:
# python3 -m ML.train_models.train_mlp

import pandas as pd
import os
import joblib
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, BatchNormalization
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau
from tensorflow.keras.optimizers import Adam
import numpy as np

from config import (
    DATA_FOR_ML_MODEL_TRAINING,
    MODEL_PATH_WHERE_MLP_MODEL_SHOULD_GET_SAVED,
    PATH_FOR_SAVING_MLP_SCALAR,
    RANDOM_STATE,
    ML_EPOCHS,
    ML_BATCH_SIZE
)
from data.prepare_data_with_scaling import prepare_data_with_scaling
from ML.evaluate_model import evaluate_model
from ma_trading_bot.ml_feature_store import get_active_feature_columns

# -------------------------------
# Reproducibility
# -------------------------------
tf.random.set_seed(RANDOM_STATE)

print('Using data file as determined in the config file to train MLP model...\n')

# -------------------------------
# Load and prepare data
# -------------------------------
data = pd.read_csv(DATA_FOR_ML_MODEL_TRAINING, index_col="Date", parse_dates=True)
feature_columns = get_active_feature_columns()
X_train_scaled, X_test_scaled, y_train, y_test, scaler, feature_names = prepare_data_with_scaling(
    data, feature_columns=feature_columns
)

print("Training class distribution:\n", pd.Series(y_train).value_counts())
print("Test class distribution:\n", pd.Series(y_test).value_counts())
print('Data prepared successfully.\n')

# -------------------------------
# Build MLP model (same as result #2)
# -------------------------------
input_dim = X_train_scaled.shape[1]
num_classes = 3  # Buy / Hold / Sell

model = Sequential([
    Dense(64, activation='relu', input_dim=input_dim),
    BatchNormalization(),
    Dropout(0.25),

    Dense(32, activation='relu'),
    BatchNormalization(),
    Dropout(0.25),

    Dense(16, activation='relu'),
    Dropout(0.2),

    Dense(num_classes, activation='softmax')
])

optimizer = Adam(learning_rate=1e-4)

model.compile(
    optimizer=optimizer,
    loss='sparse_categorical_crossentropy',
    metrics=['accuracy']
)

# -------------------------------
# Callbacks
# -------------------------------
early_stop = EarlyStopping(
    monitor='val_loss',
    patience=20,
    restore_best_weights=True
)

reduce_lr = ReduceLROnPlateau(
    monitor='val_loss',
    factor=0.5,
    patience=7,
    min_lr=1e-6,
    verbose=1
)

# -------------------------------
# Train model
# -------------------------------
history = model.fit(
    X_train_scaled,
    y_train,
    validation_split=0.2,
    epochs=ML_EPOCHS if ML_EPOCHS else 300,
    batch_size=ML_BATCH_SIZE if ML_BATCH_SIZE else 16,
    callbacks=[early_stop, reduce_lr],
    verbose=1
)

# -------------------------------
# Predictions (no threshold)
# -------------------------------
y_pred = model.predict(X_test_scaled).argmax(axis=1)

# -------------------------------
# Evaluate model
# -------------------------------
evaluate_model(y_test, y_pred)

# -------------------------------
# Save model and scaler
# -------------------------------
os.makedirs(os.path.dirname(MODEL_PATH_WHERE_MLP_MODEL_SHOULD_GET_SAVED), exist_ok=True)
os.makedirs(os.path.dirname(PATH_FOR_SAVING_MLP_SCALAR), exist_ok=True)

model.save(MODEL_PATH_WHERE_MLP_MODEL_SHOULD_GET_SAVED)
joblib.dump(scaler, PATH_FOR_SAVING_MLP_SCALAR)

print(f'\n✅ MLP model saved successfully at: {MODEL_PATH_WHERE_MLP_MODEL_SHOULD_GET_SAVED}')
print('✅ Scaler saved successfully at:', PATH_FOR_SAVING_MLP_SCALAR)
print('End of training.\n')
