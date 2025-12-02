"""
FEATURE ENGINEERING
Advanced feature creation for better predictions
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
import joblib


class FeatureEngineer:
    def __init__(self):
        self.encoders = {}
        self.scaler = None
        
    def engineer_features(self, df):
        """Create advanced features"""
        print("\n" + "="*80)
        print("🔧 FEATURE ENGINEERING")
        print("="*80)
        
        df = df.copy()
        
        # 1. Academic engagement score
        df['academic_engagement'] = (
            df.get('attendance_percentage', 50) * 0.4 +
            df.get('marks_percentage_mean', 50) * 0.3 +
            df.get('assignment_submission_rate', 50) * 0.2 +
            df.get('library_visits', 0) * 2 * 0.1
        )
        
        # 2. Financial stress indicator
        df['financial_stress'] = (
            (df.get('fee_pending_count', 0) > 0).astype(int) * 50 +
            (df.get('fee_late_count', 0) * 10)
        ).clip(0, 100)
        
        # 3. Social engagement score
        df['social_engagement'] = (
            df.get('extra_participates', 0) * 30 +
            df.get('total_activities', 0) * 20 +
            df.get('extra_leadership_roles', 0) * 30 +
            (df.get('behavior_positive_count', 0) * 10)
        ).clip(0, 100)
        
        # 4. Academic trend (improving/declining)
        if 'previous_semester_gpa' in df.columns and 'current_semester_gpa' in df.columns:
            df['gpa_change'] = df['current_semester_gpa'] - df['previous_semester_gpa'].fillna(df['current_semester_gpa'])
            df['gpa_improving'] = (df['gpa_change'] > 0).astype(int)
        else:
            df['gpa_change'] = 0
            df['gpa_improving'] = 0
        
        # 5. At-risk indicators (binary flags)
        df['flag_low_attendance'] = (df.get('attendance_percentage', 100) < 75).astype(int)
        df['flag_low_gpa'] = (df.get('cumulative_gpa', 10) < 5.0).astype(int)
        df['flag_failing_courses'] = (df.get('marks_failing_count', 0) > 0).astype(int)
        df['flag_no_activities'] = (df.get('extra_participates', 1) == 0).astype(int)
        df['flag_fee_pending'] = (df.get('fee_pending_count', 0) > 0).astype(int)
        
        df['total_risk_flags'] = (
            df['flag_low_attendance'] + df['flag_low_gpa'] + 
            df['flag_failing_courses'] + df['flag_no_activities'] + df['flag_fee_pending']
        )
        
        # 6. Learning style indicators (inferred)
        # Visual: High marks in subjects requiring diagrams (Physics, Math)
        df['learning_visual_score'] = (
            df.get('marks_subject_physics', 0) * 0.5 +
            df.get('marks_subject_mathematics', 0) * 0.5
        )
        
        # Reading/Writing: High in English, assignments
        df['learning_reading_score'] = (
            df.get('marks_subject_english', 0) * 0.5 +
            df.get('assignment_submission_rate', 0) * 0.5
        )
        
        # Kinesthetic: Sports/practical activities
        df['learning_kinesthetic_score'] = (
            df.get('extra_category_Sports', 0) * 50 +
            df.get('marks_subject_mechanical_engineering', 0) * 0.5
        )
        
        # Auditory: Cultural activities (music, debate)
        df['learning_auditory_score'] = (
            df.get('extra_category_Cultural', 0) * 50
        )
        
        print(f"✅ Created {len([c for c in df.columns if c not in df.columns])} new features")
        
        return df
    
    def encode_categorical(self, df, categorical_cols):
        """Encode categorical variables"""
        print("\n🔤 Encoding categorical variables...")
        
        df = df.copy()
        
        for col in categorical_cols:
            if col in df.columns and col != 'dropout_risk':  # Don't encode target
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.encoders[col] = le
        
        print(f"✅ Encoded {len(categorical_cols)} categorical columns")
        
        return df
    
    def scale_features(self, df, feature_cols):
        """Scale numerical features"""
        print("\n📏 Scaling numerical features...")
        
        self.scaler = StandardScaler()
        df[feature_cols] = self.scaler.fit_transform(df[feature_cols])
        
        print(f"✅ Scaled {len(feature_cols)} features")
        
        return df
    
    def save_preprocessors(self, output_dir='models'):
        """Save encoders and scaler"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        joblib.dump(self.encoders, f'{output_dir}/encoders.pkl')
        joblib.dump(self.scaler, f'{output_dir}/scaler.pkl')
        
        print(f"\n💾 Saved preprocessors to {output_dir}/")


if __name__ == "__main__":
    # Test feature engineering
    df = pd.read_csv('processed_data.csv')
    
    engineer = FeatureEngineer()
    df = engineer.engineer_features(df)
    
    print(f"\nNew features created:")
    new_cols = ['academic_engagement', 'financial_stress', 'social_engagement', 
                'total_risk_flags', 'learning_visual_score']
    print(df[new_cols].head())