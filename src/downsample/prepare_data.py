import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def get_max_sequence_length(label_info_path, primary_feature_dir, feature_column="feature_file"):
    """
    Calculate the maximum sequence length from features in the dataset.
    """
    df = pd.read_csv(label_info_path)
    max_length = 0

    for _, row in df.iterrows():
        feature_path = os.path.join(primary_feature_dir, os.path.basename(row[feature_column]))
        if not os.path.exists(feature_path):
            print(f"Warning: {feature_path} does not exist and will be skipped.")
            continue
        feature_data = np.load(feature_path)
        max_length = max(max_length, feature_data.shape[0])

    return max_length

def load_data(label_info_path, primary_feature_dir, feature_column="feature_file", label_column="class", target_length=None, weight_column="example_weight"):
    """
    Loads and flattens features, labels, and weights from .npy files, adjusting to target_length if needed.
    """
    if target_length is None:
        raise ValueError("target_length must be specified to ensure consistent feature dimensions.")

    df = pd.read_csv(label_info_path)

    # Check if 'example_weight' exists; if not, set default weights
    if weight_column not in df.columns:
        print("Warning: 'example_weight' column not found in data; setting default weight of 1 for all samples.")
        df[weight_column] = 1

    features, labels, sample_weights = [], [], []

    for _, row in df.iterrows():
        feature_path = os.path.join(primary_feature_dir, os.path.basename(row[feature_column]))
        if not os.path.exists(feature_path):
            print(f"Warning: {feature_path} does not exist and will be skipped.")
            continue
        
        feature_data = np.load(feature_path)

        # Ensure each sample has a consistent length
        if feature_data.shape[0] > target_length:  # Truncate if too long
            feature_data = feature_data[:target_length]
        elif feature_data.shape[0] < target_length:  # Pad if too short
            padding = np.zeros((target_length - feature_data.shape[0], feature_data.shape[1]))
            feature_data = np.vstack((feature_data, padding))

        # Flatten the feature array to a single vector for SVM
        features.append(feature_data.flatten())
        
        # Append the label and sample weight
        labels.append(row[label_column])
        sample_weights.append(row[weight_column])

    # Convert lists to numpy arrays
    X = np.array(features)
    y = np.array(labels)
    sample_weights = np.array(sample_weights)

    return X, y, sample_weights

def load_train_data(label_info_path="data/metadata/label_downsampled.csv", primary_feature_dir="data/downsampled_features", 
                    feature_column="contextual_feature_file", label_column="class", target_length=None, 
                    weight_column="example_weight", scaler=None):
    """
    Loads and preprocesses training data, applying feature scaling.
    """
    X_train, y_train, sample_weights = load_data(label_info_path, primary_feature_dir, feature_column, label_column, target_length, weight_column)
    if scaler is None:
        scaler = StandardScaler()
        X_train = scaler.fit_transform(X_train)
    return X_train, y_train, sample_weights, scaler

def load_eval_data(label_info_path="data/metadata/eval_downsample.csv", primary_feature_dir="data/downsampled_features", 
                   feature_column="contextual_feature_file", label_column="class", target_length=None, scaler=None):
    """
    Loads and preprocesses evaluation data.
    """
    X_eval, y_eval, _ = load_data(label_info_path, primary_feature_dir, feature_column, label_column, target_length)
    if scaler is not None:
        X_eval = scaler.transform(X_eval)
    return X_eval, y_eval

def load_test_data(label_info_path="data/metadata/test_downsample.csv", primary_feature_dir="data/downsampled_features", 
                   feature_column="contextual_feature_file", label_column="class", target_length=None, scaler=None):
    """
    Loads and preprocesses test data.
    """
    X_test, y_test, _ = load_data(label_info_path, primary_feature_dir, feature_column, label_column, target_length)
    if scaler is not None:
        X_test = scaler.transform(X_test)
    return X_test, y_test

