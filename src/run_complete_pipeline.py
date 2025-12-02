"""
COMPLETE PIPELINE EXECUTION
Run all steps in sequence
"""

import sys
import os

# Add src to path
sys.path.insert(0, 'src')

from data_loader import DataLoader
from train_model import DropoutModel
from predict_analytics import StudentAnalytics
from explainability import ModelExplainer

import pandas as pd
import json


def main():
    print("\n" + "="*80)
    print("🎓 STUDENT DROPOUT PREDICTION - COMPLETE PIPELINE")
    print("="*80)
    
    # Step 1: Load and process data
    print("\n📥 STEP 1: Loading data...")
    loader = DataLoader(data_dir='data/dummy_data')
    master_df = loader.load_all_data()
    master_df.to_csv('processed_data.csv', index=False)
    
    # Step 2: Train model
    print("\n🎯 STEP 2: Training model...")
    model = DropoutModel()
    X, y = model.prepare_data(master_df)
    X_test, y_test = model.train(X, y)
    model.save_model()
    
    # Step 3: Generate predictions
    print("\n🔮 STEP 3: Generating predictions...")
    analytics = StudentAnalytics(model_dir='models')
    results = analytics.batch_predict(master_df)
    
    # Save results
    with open('student_analytics_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    # Convert to DataFrame for CSV
    results_df = pd.DataFrame(results)
    results_df.to_csv('student_predictions.csv', index=False)
    
    # Step 4: Model explainability
    print("\n🔍 STEP 4: Generating explainability...")
    explainer_obj = ModelExplainer(model_dir='models')
    explainer, shap_values = explainer_obj.explain_model(X_test, sample_size=200)
    
    # Final summary
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETE!")
    print("="*80)
    
    print(f"\n📊 Results Summary:")
    print(f"   Total students: {len(results)}")
    print(f"   High Risk: {sum(1 for r in results if r['dropout_risk'] == 'High Risk')}")
    print(f"   Medium Risk: {sum(1 for r in results if r['dropout_risk'] == 'Medium Risk')}")
    print(f"   Low Risk: {sum(1 for r in results if r['dropout_risk'] == 'Low Risk')}")
    
    print(f"\n💾 Output Files:")
    print(f"   - processed_data.csv (master dataset)")
    print(f"   - models/dropout_model.pkl (trained model)")
    print(f"   - student_analytics_results.json (detailed analytics)")
    print(f"   - student_predictions.csv (predictions table)")
    print(f"   - models/feature_importance.png")
    print(f"   - models/shap_importance.png")
    print(f"   - models/shap_summary.png")
    
    # Sample result
    print(f"\n📋 Sample Student Analytics:")
    print(json.dumps(results[0], indent=2))
    
    print("\n🎉 ALL DONE!")


if __name__ == "__main__":
    main()