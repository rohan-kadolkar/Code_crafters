"""
PREDICTION & ANALYTICS
Generate predictions and comprehensive student analytics
OPTIMIZED FOR BATCH PROCESSING
"""

import pandas as pd
import numpy as np
import joblib
import json
from feature_engineering import FeatureEngineer


class StudentAnalytics:
    def __init__(self, model_dir='models'):
        """Load trained model and preprocessors"""
        self.model = joblib.load(f'{model_dir}/dropout_model.pkl')
        self.scaler = joblib.load(f'{model_dir}/scaler.pkl')
        self.encoders = joblib.load(f'{model_dir}/encoders.pkl')
        self.feature_names = joblib.load(f'{model_dir}/feature_names.pkl')
        self.label_mapping = {0: 'Low Risk', 1: 'Medium Risk', 2: 'High Risk'}
        
        # Initialize feature engineer
        self.feature_engineer = FeatureEngineer()
        self.feature_engineer.encoders = self.encoders
        self.feature_engineer.scaler = self.scaler
    
    def batch_predict(self, df):
        """
        Predict for multiple students efficiently (OPTIMIZED)
        Process entire dataframe at once instead of row-by-row
        """
        print(f"\n🔮 Processing {len(df)} students in batch mode...")
        
        # Store student IDs and original data for analytics
        student_ids = df['student_id'].values
        
        # 1. Engineer features for entire dataframe at once
        print("🔧 Engineering features for all students...")
        df_processed = self.feature_engineer.engineer_features(df.copy())
        
        # 2. Prepare features (same as training)
        X = df_processed[self.feature_names].copy()
        
        # 3. Encode categorical
        categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
        for col in categorical_cols:
            if col in self.encoders:
                X[col] = self.encoders[col].transform(X[col].astype(str))
        
        # 4. Handle missing values
        X.fillna(0, inplace=True)
        
        # 5. Scale features
        numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        X_scaled = X.copy()
        X_scaled[numeric_cols] = self.scaler.transform(X[numeric_cols])
        
        # 6. Batch predictions
        print("🎯 Generating predictions...")
        predictions = self.model.predict(X_scaled)
        probabilities = self.model.predict_proba(X_scaled)
        
        # 7. Generate analytics for each student
        print("📊 Generating individual analytics...")
        results = []
        
        for idx in range(len(df_processed)):
            student_data = df_processed.iloc[idx]
            prediction = predictions[idx]
            probs = probabilities[idx]
            
            dropout_risk = self.label_mapping[prediction]
            risk_confidence = probs[prediction] * 100
            
            # Generate analytics
            analytics = self._generate_analytics(student_data)
            
            # Compile results - CONVERT ALL NUMPY TYPES TO PYTHON TYPES
            result = {
                'student_id': int(student_ids[idx]),
                'dropout_risk': str(dropout_risk),
                'risk_confidence': float(round(risk_confidence, 2)),
                'risk_probabilities': {
                    'Low Risk': float(round(probs[0] * 100, 2)),
                    'Medium Risk': float(round(probs[1] * 100, 2)),
                    'High Risk': float(round(probs[2] * 100, 2))
                },
                'learning_style': str(analytics['learning_style']),
                'strengths': [str(s) for s in analytics['strengths']],
                'weaknesses': [str(w) for w in analytics['weaknesses']],
                'interests': [str(i) for i in analytics['interests']],
                'recommendations': [str(r) for r in self._generate_recommendations(dropout_risk, analytics)]
            }
            
            results.append(result)
            
            # Progress indicator
            if (idx + 1) % 100 == 0:
                print(f"   Processed {idx + 1}/{len(df_processed)} students...")
        
        print(f"✅ Completed predictions for {len(results)} students")
        
        return results
    
    def predict_student(self, student_data):
        """
        Predict dropout risk and generate analytics for a single student
        
        Args:
            student_data: dict or DataFrame row with student features
            
        Returns:
            dict with predictions and analytics
        """
        # Convert to DataFrame if dict
        if isinstance(student_data, dict):
            df = pd.DataFrame([student_data])
        else:
            df = pd.DataFrame([student_data.to_dict()])
        
        # Use batch_predict for single student
        results = self.batch_predict(df)
        return results[0] if results else None
    
    def _generate_analytics(self, student):
        """Generate individual student analytics"""
        
        # 1. Learning Style (inferred from scores)
        learning_scores = {
            'Visual': student.get('learning_visual_score', 0),
            'Reading/Writing': student.get('learning_reading_score', 0),
            'Kinesthetic': student.get('learning_kinesthetic_score', 0),
            'Auditory': student.get('learning_auditory_score', 0)
        }
        learning_style = max(learning_scores, key=learning_scores.get)
        
        # 2. Academic Strengths (top performing subjects)
        subject_cols = [col for col in student.index if col.startswith('marks_subject_')]
        if subject_cols:
            subject_scores = {col.replace('marks_subject_', '').replace('_', ' ').title(): 
                            student[col] for col in subject_cols}
            sorted_subjects = sorted(subject_scores.items(), key=lambda x: x[1], reverse=True)
            strengths = [subj for subj, score in sorted_subjects[:3] if score > 60]
        else:
            strengths = []
        
        # Add other strengths
        if student.get('attendance_percentage', 0) >= 85:
            strengths.append('Excellent Attendance')
        if student.get('assignment_submission_rate', 0) >= 90:
            strengths.append('Assignment Completion')
        if student.get('extra_leadership_roles', 0) > 0:
            strengths.append('Leadership')
        
        # 3. Weaknesses
        weaknesses = []
        
        # Low performing subjects
        if subject_cols:
            weak_subjects = [subj for subj, score in sorted_subjects[-2:] if score < 50]
            weaknesses.extend(weak_subjects)
        
        # Low attendance
        if student.get('attendance_percentage', 100) < 75:
            weaknesses.append('Low Attendance')
        
        # Low assignment completion
        if student.get('assignment_submission_rate', 100) < 70:
            weaknesses.append('Assignment Delays')
        
        # Fee issues
        if student.get('fee_pending_count', 0) > 0:
            weaknesses.append('Pending Fees')
        
        # No extracurricular
        if student.get('extra_participates', 1) == 0:
            weaknesses.append('No Extracurricular Activities')
        
        # 4. Interests (from extracurricular activities)
        interests = []
        
        # Check activity categories
        activity_cats = ['Technical', 'Sports', 'Cultural', 'Social', 'Academic']
        for cat in activity_cats:
            col = f'extra_category_{cat}'
            if student.get(col, 0) > 0:
                interests.append(cat)
        
        # Check library usage
        if student.get('library_visits', 0) > 10:
            interests.append('Reading/Research')
        
        # Check specific subjects
        if student.get('marks_subject_computer_science', 0) > 75:
            interests.append('Computer Science')
        
        return {
            'learning_style': learning_style,
            'strengths': strengths[:5] if strengths else ['None identified'],
            'weaknesses': weaknesses[:5] if weaknesses else ['None identified'],
            'interests': interests[:5] if interests else ['None identified']
        }
    
    def _generate_recommendations(self, risk_level, analytics):
        """Generate personalized recommendations"""
        recommendations = []
        
        if risk_level == 'High Risk':
            recommendations.append("🚨 URGENT: Schedule immediate counseling session")
            recommendations.append("👥 Assign dedicated faculty mentor")
            recommendations.append("📞 Contact family regarding support")
        
        if risk_level in ['High Risk', 'Medium Risk']:
            recommendations.append("📚 Recommend tutoring for weak subjects")
            recommendations.append("⏰ Set weekly check-in meetings")
        
        # Specific recommendations based on weaknesses
        if 'Low Attendance' in analytics['weaknesses']:
            recommendations.append("📅 Address attendance issues - provide flexible options")
        
        if 'No Extracurricular Activities' in analytics['weaknesses']:
            recommendations.append("🎯 Encourage joining 1-2 clubs/activities")
        
        if 'Pending Fees' in analytics['weaknesses']:
            recommendations.append("💰 Discuss financial aid/scholarship options")
        
        # Leverage strengths
        if analytics['strengths'] and analytics['strengths'][0] != 'None identified':
            recommendations.append(f"💪 Leverage strengths: {', '.join(analytics['strengths'][:2])}")
        
        if risk_level == 'Low Risk':
            recommendations.append("✅ Continue current performance")
            recommendations.append("🌟 Consider peer mentoring opportunities")
        
        return recommendations[:6]  # Top 6 recommendations


if __name__ == "__main__":
    import os
    
    # Load test data
    df = pd.read_csv('processed_data.csv')
    
    # Initialize analytics
    models_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
    analytics = StudentAnalytics(model_dir=models_dir)
    
    # Predict for all students (OPTIMIZED - batch mode)
    print("🔮 Generating predictions for all students...")
    results = analytics.batch_predict(df)
    
    # Save results
    output_dir = os.path.dirname(os.path.dirname(__file__))
    results_path = os.path.join(output_dir, 'student_analytics_results.json')
    
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✅ Predictions complete: {len(results)} students")
    print(f"💾 Results saved: {results_path}")
    
    # Display sample
    print("\n📋 Sample Results (First 3):")
    for i in range(min(3, len(results))):
        print(f"\n{'-'*60}")
        print(f"Student ID: {results[i]['student_id']}")
        print(f"Risk: {results[i]['dropout_risk']} ({results[i]['risk_confidence']:.1f}%)")
        print(f"Learning Style: {results[i]['learning_style']}")
        print(f"Strengths: {', '.join(results[i]['strengths'][:3])}")