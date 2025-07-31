from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, precision_score, recall_score, f1_score
def evaluate_model(y_test, y_pred):
    print("\nClassification Report:\n", classification_report(y_test, y_pred))
    print("\n Confusion Matrix:\n", confusion_matrix(y_test, y_pred), '\n\n')
    print(" Model Performance on Test Set:")
    print(f" Accuracy:  {accuracy_score(y_test, y_pred):.4f}")
    print(f" Precision: {precision_score(y_test, y_pred, average='weighted'):.4f}")
    print(f" Recall:    {recall_score(y_test, y_pred, average='weighted'):.4f}")
    print(f" F1 Score:  {f1_score(y_test, y_pred, average='weighted'):.4f}\n\n\n")