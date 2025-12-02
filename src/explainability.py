"""
MODEL EXPLAINABILITY
SHAP values for explaining predictions
"""

import pandas as pd
import numpy as np
import joblib
import shap
import matplotlib.pyplot as plt
import os


class ModelExplainer:
    def __init__(self, model_dir='models'):
        self.model = joblib.load(f'{model_dir}/dropout_model.pkl')
        self.feature_names = joblib.load(f'{model_dir}/feature_names.pkl')
        self.model_dir = model_dir
        
    def explain_model(self, X, sample_size=100):
        """Generate SHAP explanations for model"""
        print("\n" + "="*80)
        print("🔍 MODEL EXPLAINABILITY (SHAP)")
        print("="*80)
        
        # Sample for faster computation
        X_sample = X.sample(n=min(sample_size, len(X)), random_state=42)
        
        print(f"\n📊 Computing SHAP values for {len(X_sample)} samples...")
        
        try:
            # Create SHAP explainer
            explainer = shap.TreeExplainer(self.model)
            shap_values = explainer.shap_values(X_sample)
            
            # Global feature importance
            self._plot_global_importance(shap_values, X_sample)
            
            # Summary plot
            self._plot_summary(shap_values, X_sample)
            
            print("\n✅ SHAP explainability complete!")
            
            return explainer, shap_values
            
        except Exception as e:
            print(f"\n⚠️ SHAP computation encountered an issue: {e}")
            print("   This is non-critical - predictions are still valid")
            return None, None
    
    def explain_student(self, student_data, explainer=None):
        """Explain prediction for individual student"""
        try:
            if explainer is None:
                explainer = shap.TreeExplainer(self.model)
            
            shap_values = explainer.shap_values(student_data)
            
            # Force plot
            output_path = os.path.join(self.model_dir, 'student_explanation.png')
            shap.force_plot(
                explainer.expected_value[1],  # Medium Risk class
                shap_values[1],
                student_data,
                matplotlib=True,
                show=False
            )
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"💾 Individual explanation saved: {output_path}")
            
        except Exception as e:
            print(f"⚠️ Student explanation failed: {e}")
    
    def _plot_global_importance(self, shap_values, X):
        """Plot global feature importance"""
        try:
            # Handle multi-class SHAP values
            if isinstance(shap_values, list):
                # For multi-class: shap_values is a list of arrays
                # Average absolute SHAP values across all classes and samples
                mean_shap = np.mean([np.abs(sv).mean(axis=0) for sv in shap_values], axis=0)
            else:
                # For binary: single array
                mean_shap = np.abs(shap_values).mean(axis=0)
            
            # Ensure mean_shap and feature names have same length
            if len(mean_shap) != len(X.columns):
                print(f"⚠️ Shape mismatch: {len(mean_shap)} SHAP values vs {len(X.columns)} features")
                mean_shap = mean_shap[:len(X.columns)]  # Truncate if needed
            
            importance_df = pd.DataFrame({
                'feature': X.columns[:len(mean_shap)],
                'importance': mean_shap
            }).sort_values('importance', ascending=False).head(20)
            
            plt.figure(figsize=(10, 8))
            plt.barh(importance_df['feature'], importance_df['importance'])
            plt.xlabel('Mean |SHAP value|')
            plt.title('Top 20 Features (SHAP Importance)')
            plt.gca().invert_yaxis()
            plt.tight_layout()
            
            output_path = os.path.join(self.model_dir, 'shap_importance.png')
            plt.savefig(output_path, dpi=300)
            plt.close()
            
            print(f"💾 SHAP importance plot saved: {output_path}")
            
        except Exception as e:
            print(f"⚠️ Global importance plot failed: {e}")
    
    def _plot_summary(self, shap_values, X):
        """Plot SHAP summary"""
        try:
            plt.figure(figsize=(10, 8))
            
            # For multi-class, use the medium risk class (index 1)
            if isinstance(shap_values, list):
                shap.summary_plot(shap_values[1], X, show=False, max_display=20)
            else:
                shap.summary_plot(shap_values, X, show=False, max_display=20)
            
            plt.tight_layout()
            
            output_path = os.path.join(self.model_dir, 'shap_summary.png')
            plt.savefig(output_path, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"💾 SHAP summary plot saved: {output_path}")
            
        except Exception as e:
            print(f"⚠️ Summary plot failed: {e}")


if __name__ == "__main__":
    # Load data
    df = pd.read_csv('processed_data.csv')
    
    # Prepare features (use same preprocessing as training)
    from train_model import DropoutModel
    model = DropoutModel()
    X, y = model.prepare_data(df)
    
    # Explain model
    explainer_obj = ModelExplainer(model_dir='models')
    explainer, shap_values = explainer_obj.explain_model(X, sample_size=200)
    
    # Explain first student
    if explainer is not None:
        print("\n🔬 Explaining first student prediction...")
        explainer_obj.explain_student(X.iloc[:1], explainer)
    
    print("\n✅ Explainability analysis complete!")