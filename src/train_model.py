"""
MODEL TRAINING
Train XGBoost classifier for dropout prediction with hyperparameter tuning
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score
from xgboost import XGBClassifier
from imblearn.over_sampling import SMOTE
import joblib
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
import os
warnings.filterwarnings('ignore')

from feature_engineering import FeatureEngineer


class DropoutModel:
    def __init__(self):
        self.model = None
        self.feature_engineer = FeatureEngineer()
        self.feature_names = None
        self.label_mapping = {'Low Risk': 0, 'Medium Risk': 1, 'High Risk': 2}
        
    def prepare_data(self, df):
        """Prepare data for training"""
        print("\n" + "="*80)
        print("📊 DATA PREPARATION")
        print("="*80)
        
        # Engineer features
        df = self.feature_engineer.engineer_features(df)
        
        # Select features
        feature_cols = self._select_features(df)
        
        # Encode target
        df['dropout_risk_encoded'] = df['dropout_risk'].map(self.label_mapping)
        
        # Separate features and target
        X = df[feature_cols]
        y = df['dropout_risk_encoded']
        
        # Encode categorical features
        categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
        X = self.feature_engineer.encode_categorical(X, categorical_cols)
        
        # Handle any remaining NaN
        X.fillna(0, inplace=True)
        
        # Scale features
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        X = self.feature_engineer.scale_features(X, numeric_cols)
        
        self.feature_names = X.columns.tolist()
        
        print(f"\n✅ Features selected: {len(self.feature_names)}")
        print(f"✅ Target distribution:")
        print(y.value_counts())
        
        return X, y
    
    def _select_features(self, df):
        """Select relevant features for modeling"""
        # Exclude non-feature columns
        exclude_cols = [
            'student_id', 'roll_number', 'first_name', 'last_name', 'full_name',
            'email', 'phone', 'date_of_birth', 'admission_date', 'registration_date',
            'dropout_risk', 'dropout_risk_score', 'dropout_risk_encoded',
            'father_name', 'mother_name', 'guardian_contact', 'permanent_address'
        ]
        
        feature_cols = [col for col in df.columns if col not in exclude_cols]
        
        # Keep only numeric and key categorical
        keep_categorical = ['gender', 'location_type', 'branch', 'income_level', 
                           'gpa_trend', 'academic_standing', 'registration_status']
        
        feature_cols = [col for col in feature_cols if 
                       col in keep_categorical or 
                       df[col].dtype in [np.int64, np.float64]]
        
        return feature_cols
    
    def train(self, X, y, test_size=0.2, handle_imbalance=True):
        """Train the model"""
        print("\n" + "="*80)
        print("🎯 MODEL TRAINING")
        print("="*80)
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        print(f"\n📊 Train size: {len(X_train)}, Test size: {len(X_test)}")
        
        # Handle class imbalance with SMOTE
        if handle_imbalance:
            print("\n⚖️ Handling class imbalance with SMOTE...")
            smote = SMOTE(random_state=42)
            X_train, y_train = smote.fit_resample(X_train, y_train)
            print(f"✅ Resampled train size: {len(X_train)}")
        
        # Train XGBoost
        print("\n🚀 Training XGBoost Classifier...")
        
        self.model = XGBClassifier(
            n_estimators=200,
            max_depth=6,
            learning_rate=0.1,
            subsample=0.8,
            colsample_bytree=0.8,
            objective='multi:softmax',
            num_class=3,
            random_state=42,
            eval_metric='mlogloss'
        )
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Evaluate
        self._evaluate(X_test, y_test)
        
        return X_test, y_test
    
    def _evaluate(self, X_test, y_test):
        """Evaluate model performance"""
        print("\n" + "="*80)
        print("📈 MODEL EVALUATION")
        print("="*80)
        
        y_pred = self.model.predict(X_test)
        y_prob = self.model.predict_proba(X_test)
        
        # Accuracy
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\n🎯 Accuracy: {accuracy:.4f}")
        
        # Classification Report
        print("\n📋 Classification Report:")
        target_names = ['Low Risk', 'Medium Risk', 'High Risk']
        print(classification_report(y_test, y_pred, target_names=target_names))
        
        # Confusion Matrix
        print("\n🔢 Confusion Matrix:")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        # ROC-AUC (one-vs-rest)
        try:
            roc_auc = roc_auc_score(y_test, y_prob, multi_class='ovr')
            print(f"\n📊 ROC-AUC Score: {roc_auc:.4f}")
        except:
            print("\n⚠️ ROC-AUC calculation skipped (needs more samples per class)")
        
        # Feature Importance
        self._plot_feature_importance()
    
    def _plot_feature_importance(self, top_n=20):
        """Plot top feature importances"""
        importance_df = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False).head(top_n)
        
        plt.figure(figsize=(10, 8))
        sns.barplot(data=importance_df, x='importance', y='feature')
        plt.title(f'Top {top_n} Feature Importances')
        plt.xlabel('Importance')
        plt.tight_layout()
        # plt.savefig('models/feature_importance.png', dpi=300)error line
        output_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                               'models', 'feature_importance.png')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        plt.savefig(output_path, dpi=300)
        plt.close()
        # print(f"\n💾 Feature importance plot saved: models/feature_importance.png") error line
        print(f"\n💾 Feature importance plot saved: {output_path}")
    
    def save_model(self, output_dir='models'):
        """Save trained model and preprocessors"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        joblib.dump(self.model, f'{output_dir}/dropout_model.pkl')
        self.feature_engineer.save_preprocessors(output_dir)
        joblib.dump(self.feature_names, f'{output_dir}/feature_names.pkl')
        
        print(f"\n💾 Model saved to {output_dir}/")


if __name__ == "__main__":
    # Load processed data
    df = pd.read_csv('processed_data.csv')
    
    # Initialize and train
    model = DropoutModel()
    X, y = model.prepare_data(df)
    X_test, y_test = model.train(X, y)
    model.save_model()
    
    print("\n🎉 Training complete!")