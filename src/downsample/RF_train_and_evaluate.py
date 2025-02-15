import prepare_data
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score
from sklearn.ensemble import RandomForestClassifier
from sklearn.utils.class_weight import compute_class_weight
from joblib import dump
import numpy as np
import os
import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc



def evaluate_model_with_threshold(model, X_eval, y_eval, threshold=0.1):
    """Evaluate Random Forest model with an adjustable decision threshold."""
    y_scores = model.predict_proba(X_eval)[:, 1]  # Probabilities for the positive class
    y_eval_pred = (y_scores > threshold).astype(int)  # Apply threshold

    accuracy = accuracy_score(y_eval, y_eval_pred)
    precision = precision_score(y_eval, y_eval_pred, average='binary')
    recall = recall_score(y_eval, y_eval_pred, average='binary')
    f1 = f1_score(y_eval, y_eval_pred, average='binary')

    print(classification_report(y_eval, y_eval_pred))
    print(f"Threshold: {threshold}")
    print(f"Accuracy: {accuracy}, Precision: {precision}, Recall: {recall}, F1 Score: {f1}")
    return accuracy, precision, recall, f1


def main():
    # Calculate target_length from training data
    target_length = prepare_data.get_max_sequence_length(
        label_info_path="data/metadata/label_downsampled.csv",
        primary_feature_dir="data/downsampled_features"
    )
    print(f"Using target length of {target_length} based on maximum sequence length in training data.")

    # Load training data
    X_train, y_train, sample_weights_train, scaler = prepare_data.load_train_data(
        label_info_path="data/metadata/train_downsample.csv",
        primary_feature_dir="data/downsampled_features",
        target_length=target_length
    )

    # Load evaluation data
    X_eval, y_eval = prepare_data.load_eval_data(
        label_info_path="data/metadata/eval_downsample.csv",
        primary_feature_dir="data/downsampled_features",
        target_length=target_length,
        scaler=scaler
    )

    # Compute class weights for imbalanced data
    class_weights = compute_class_weight(class_weight='balanced', classes=np.unique(y_train), y=y_train)
    class_weight_dict = dict(enumerate(class_weights))

    # Train the baseline Random Forest model
    print("\nTraining baseline Random Forest model with 100 trees and max depth of None")
    baseline_model = RandomForestClassifier(
        n_estimators=100, max_depth=None, random_state=42, class_weight=class_weight_dict
    )
    baseline_model.fit(X_train, y_train, sample_weight=sample_weights_train)

    # Print the classification report on training data
    y_train_pred = baseline_model.predict(X_train)
    print("\nClassification Report for the baseline Random Forest model on training data:")
    print(classification_report(y_train, y_train_pred))

    # Evaluate the baseline model on evaluation data with a custom threshold
    print("\nEvaluation Results for the baseline Random Forest model on evaluation data:")
    baseline_threshold = 0.5  # Set baseline threshold (default for Random Forests)
    _, _, _, f1 = evaluate_model_with_threshold(baseline_model, X_eval, y_eval, threshold=baseline_threshold)

    # Save the trained model
   
    print(f"\nBest model saved as 'best_rf_model.joblib' with F1 Score: {f1}")
    
    # draw ROC curve
    y_eval_prob = baseline_model.predict_proba(X_eval)[:, 1]
    fpr, tpr, thresholds = roc_curve(y_eval, y_eval_prob)
    roc_auc = auc(fpr, tpr)

    # Plot the ROC curve
    plt.figure()
    plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC curve (AUC = {roc_auc:.2f})')
    plt.plot([0, 1], [0, 1], color='gray', lw=2, linestyle='--', label='Random Guess')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic (ROC) Curve')
    plt.legend(loc="lower right")

    # Save the plot
    output_dir = "data/visualization"
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "roc_auc_curve_RD_DOWN.png")
    plt.savefig(output_path)
    plt.close()
    
    # Feature importance ranking
    importances = baseline_model.feature_importances_
    # Restrict to top 20 features
    indices = np.argsort(importances)[::-1][:20]
    print("Feature ranking:")
    for f in range(len(indices)):  # Fix: Iterate only over available top indices
        print(f"{f + 1}. feature {indices[f]} ({importances[indices[f]]})")
    
    # Save feature importances to a CSV file
    feature_importance = [[indices[f], importances[indices[f]]] for f in range(len(indices))]
    output_csv_path = os.path.join(output_dir, "feature_importance_downsampled.csv")
    np.savetxt(output_csv_path, feature_importance, delimiter=",", fmt='%s', header="Feature,Importance")
    
    # Save the model
    output_dir = "data/visualization"
    dump(baseline_model, 'models/baseline_model/best_rf_model.joblib')




if __name__ == "__main__":
    main()
