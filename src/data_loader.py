"""
DATA LOADER - Load and merge all CSV files
Handles missing values and creates master dataset
"""

import pandas as pd
import numpy as np
import os
from datetime import datetime


class DataLoader:
    def __init__(self, data_dir='data/dummy_data'):
        self.data_dir = data_dir
        
    def load_all_data(self):
        """Load and merge all CSV files"""
        print("="*80)
        print("📊 LOADING ALL DATA FILES")
        print("="*80)
        
        # 1. Load base tables
        students = pd.read_csv(f'{self.data_dir}/01_students_master.csv')
        family = pd.read_csv(f'{self.data_dir}/02_family_background.csv')
        academic = pd.read_csv(f'{self.data_dir}/03_academic_history.csv')
        attendance = pd.read_csv(f'{self.data_dir}/04_daily_attendance.csv')
        marks = pd.read_csv(f'{self.data_dir}/05_marks_exams.csv')
        assignments = pd.read_csv(f'{self.data_dir}/06_assignments.csv')
        behavior = pd.read_csv(f'{self.data_dir}/07_behavior_reports.csv')
        library = pd.read_csv(f'{self.data_dir}/08_library_usage.csv')
        fees = pd.read_csv(f'{self.data_dir}/09_fee_payments.csv')
        extra_reg = pd.read_csv(f'{self.data_dir}/10_extracurricular_registrations.csv')
        extra_details = pd.read_csv(f'{self.data_dir}/11_extracurricular_details.csv')
        extra_attendance = pd.read_csv(f'{self.data_dir}/12_extracurricular_attendance.csv')
        
        print(f"✅ Loaded {len(students)} students")
        
        # 2. Aggregate features from transactional tables
        print("\n🔄 Aggregating features...")
        
        # Attendance metrics
        attendance_agg = self._aggregate_attendance(attendance)
        
        # Marks metrics
        marks_agg = self._aggregate_marks(marks)
        
        # Assignment metrics
        assignment_agg = self._aggregate_assignments(assignments)
        
        # Behavior metrics
        behavior_agg = self._aggregate_behavior(behavior)
        
        # Library metrics
        library_agg = self._aggregate_library(library)
        
        # Fee metrics
        fee_agg = self._aggregate_fees(fees)
        
        # Extracurricular metrics
        extra_agg = self._aggregate_extracurricular(extra_reg, extra_details, extra_attendance)
        
        # 3. Merge everything
        print("\n🔗 Merging all features...")
        master_df = students.copy()
        
        for df_to_merge in [family, academic, attendance_agg, marks_agg, assignment_agg, 
                           behavior_agg, library_agg, fee_agg, extra_agg]:
            master_df = master_df.merge(df_to_merge, on='student_id', how='left')
        
        print(f"✅ Master dataset created: {master_df.shape}")
        
        # 4. Handle missing values
        master_df = self._handle_missing_values(master_df)
        
        # 5. Create target variable (dropout risk)
        master_df = self._create_target_variable(master_df)
        
        return master_df
    
    def _aggregate_attendance(self, df):
        """Aggregate attendance metrics"""
        agg = df.groupby('student_id').agg({
            'status': [
                ('attendance_total_days', 'count'),
                ('attendance_present_days', lambda x: (x == 'Present').sum()),
                ('attendance_absent_days', lambda x: (x == 'Absent').sum())
            ]
        })
        agg.columns = ['_'.join(col).strip() for col in agg.columns.values]
        agg.reset_index(inplace=True)
        
        # Calculate percentage
        agg['attendance_percentage'] = (agg['status_attendance_present_days'] / 
                                        agg['status_attendance_total_days'] * 100)
        
        # Attendance trend (first 4 weeks vs last 4 weeks)
        first_half = df[df['week_number'] <= 4].groupby('student_id')['status'].apply(
            lambda x: (x == 'Present').sum() / len(x) * 100
        ).rename('attendance_first_half')
        
        second_half = df[df['week_number'] > 4].groupby('student_id')['status'].apply(
            lambda x: (x == 'Present').sum() / len(x) * 100
        ).rename('attendance_second_half')
        
        agg = agg.merge(first_half, on='student_id', how='left')
        agg = agg.merge(second_half, on='student_id', how='left')
        
        agg['attendance_trend'] = agg['attendance_second_half'] - agg['attendance_first_half']
        
        return agg
    
    def _aggregate_marks(self, df):
        """Aggregate marks metrics"""
        agg = df.groupby('student_id').agg({
            'percentage': ['mean', 'std', 'min', 'max'],
            'obtained_marks': 'sum'
        })
        agg.columns = ['marks_' + '_'.join(col).strip() for col in agg.columns.values]
        agg.reset_index(inplace=True)
        
        # Subject-wise performance
        subject_perf = df.groupby(['student_id', 'subject'])['percentage'].mean().unstack(fill_value=0)
        subject_perf.columns = ['marks_subject_' + col.lower().replace(' ', '_') for col in subject_perf.columns]
        subject_perf.reset_index(inplace=True)
        
        agg = agg.merge(subject_perf, on='student_id', how='left')
        
        # Failing subjects count
        failing = df[df['percentage'] < 40].groupby('student_id').size().rename('marks_failing_count')
        agg = agg.merge(failing, on='student_id', how='left')
        agg['marks_failing_count'].fillna(0, inplace=True)
        
        return agg
    
    def _aggregate_assignments(self, df):
        """Aggregate assignment metrics"""
        agg = df.groupby('student_id').agg({
            'submitted': lambda x: (x == 'Yes').sum() / len(x) * 100,
            'status': lambda x: (x == 'Late').sum()
        })
        agg.columns = ['assignment_submission_rate', 'assignment_late_count']
        agg.reset_index(inplace=True)
        
        # Grade distribution
        grade_counts = pd.get_dummies(df['grade'], prefix='assignment_grade')
        grade_counts['student_id'] = df['student_id']
        grade_agg = grade_counts.groupby('student_id').sum()
        agg = agg.merge(grade_agg, on='student_id', how='left')
        
        return agg
    
    def _aggregate_behavior(self, df):
        """Aggregate behavior metrics"""
        if df.empty:
            return pd.DataFrame({'student_id': [], 'behavior_positive_count': [], 
                               'behavior_negative_count': []})
        
        agg = df.groupby(['student_id', 'behavior_type']).size().unstack(fill_value=0)
        agg.columns = ['behavior_' + col.lower() + '_count' for col in agg.columns]
        agg.reset_index(inplace=True)
        
        if 'behavior_positive_count' not in agg.columns:
            agg['behavior_positive_count'] = 0
        if 'behavior_negative_count' not in agg.columns:
            agg['behavior_negative_count'] = 0
        
        agg['behavior_total_count'] = agg['behavior_positive_count'] + agg['behavior_negative_count']
        
        return agg
    
    def _aggregate_library(self, df):
        """Aggregate library metrics"""
        if df.empty:
            return pd.DataFrame({'student_id': [], 'library_visits': [], 
                               'library_hours': []})
        
        agg = df.groupby('student_id').agg({
            'visit_date': 'count',
            'duration_hours': 'sum'
        })
        agg.columns = ['library_visits', 'library_hours']
        agg.reset_index(inplace=True)
        agg['library_hours'].fillna(0, inplace=True)
        
        return agg
    
    def _aggregate_fees(self, df):
        """Aggregate fee metrics"""
        agg = df.groupby('student_id').agg({
            'amount_paid': 'sum',
            'status': lambda x: (x.str.contains('Pending')).sum()
        })
        agg.columns = ['fee_total_paid', 'fee_pending_count']
        agg.reset_index(inplace=True)
        
        # Late payment count
        late = df[df['status'].str.contains('Late', na=False)].groupby('student_id').size().rename('fee_late_count')
        agg = agg.merge(late, on='student_id', how='left')
        agg['fee_late_count'].fillna(0, inplace=True)
        
        return agg
    
    def _aggregate_extracurricular(self, reg_df, details_df, attendance_df):
        """Aggregate extracurricular metrics"""
        # Registration summary
        agg = reg_df[['student_id', 'total_activities']].copy()
        agg['extra_participates'] = (reg_df['participation_status'] == 'Active').astype(int)
        
        # Details aggregation
        if not details_df.empty:
            # Activity categories
            categories = pd.get_dummies(details_df['activity_category'], prefix='extra_category')
            categories['student_id'] = details_df['student_id']
            cat_agg = categories.groupby('student_id').sum()
            agg = agg.merge(cat_agg, on='student_id', how='left')
            
            # Leadership roles
            leadership = details_df[details_df['role'].isin(['Coordinator', 'President/Head'])]
            leadership_count = leadership.groupby('student_id').size().rename('extra_leadership_roles')
            agg = agg.merge(leadership_count, on='student_id', how='left')
            agg['extra_leadership_roles'].fillna(0, inplace=True)
            
            # Average hours per week
            hours = details_df.groupby('student_id')['hours_per_week'].mean().rename('extra_hours_per_week')
            agg = agg.merge(hours, on='student_id', how='left')
            
            # Total events
            events = details_df.groupby('student_id')['total_events_participated'].sum().rename('extra_total_events')
            agg = agg.merge(events, on='student_id', how='left')
        
        # Attendance aggregation
        if not attendance_df.empty:
            extra_attendance = attendance_df.groupby('student_id').agg({
                'attendance_status': [
                    ('extra_sessions_total', 'count'),
                    ('extra_sessions_present', lambda x: (x == 'Present').sum())
                ]
            })
            extra_attendance.columns = ['_'.join(col).strip() for col in extra_attendance.columns.values]
            extra_attendance.reset_index(inplace=True)
            extra_attendance['extra_attendance_percentage'] = (
                extra_attendance['attendance_status_extra_sessions_present'] / 
                extra_attendance['attendance_status_extra_sessions_total'] * 100
            )
            agg = agg.merge(extra_attendance, on='student_id', how='left')
        
        # Fill NaN
        agg.fillna(0, inplace=True)
        
        return agg
    
    def _handle_missing_values(self, df):
        """Handle missing values intelligently"""
        print("\n🔧 Handling missing values...")
        
        # Fill numeric columns with 0 or median
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        for col in numeric_cols:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].median(), inplace=True)
        
        # Fill categorical with mode or 'Unknown'
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            if df[col].isnull().sum() > 0:
                df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'Unknown', inplace=True)
        
        print(f"✅ Missing values handled")
        return df
    
    def _create_target_variable(self, df):
        """
        Create dropout risk target based on multiple factors
        
        Risk Factors:
        - Low GPA (< 5.0)
        - Low attendance (< 75%)
        - Failing courses
        - Fee delays
        - No extracurricular participation
        - Declining trends
        """
        print("\n🎯 Creating target variable (dropout_risk)...")
        
        risk_score = 0
        
        # GPA risk (30% weight)
        if 'cumulative_gpa' in df.columns:
            risk_score += np.where(df['cumulative_gpa'] < 4.0, 30, 
                                  np.where(df['cumulative_gpa'] < 5.5, 20,
                                          np.where(df['cumulative_gpa'] < 7.0, 10, 0)))
        
        # Attendance risk (25% weight)
        if 'attendance_percentage' in df.columns:
            risk_score += np.where(df['attendance_percentage'] < 60, 25,
                                  np.where(df['attendance_percentage'] < 75, 15, 0))
        
        # Credit completion risk (20% weight)
        if 'credit_completion_rate' in df.columns:
            risk_score += np.where(df['credit_completion_rate'] < 60, 20,
                                  np.where(df['credit_completion_rate'] < 80, 10, 0))
        
        # Fee payment risk (10% weight)
        if 'fee_pending_count' in df.columns:
            risk_score += np.where(df['fee_pending_count'] > 1, 10,
                                  np.where(df['fee_pending_count'] > 0, 5, 0))
        
        # Extracurricular risk (10% weight)
        if 'extra_participates' in df.columns:
            risk_score += np.where(df['extra_participates'] == 0, 10, 0)
        
        # Declining trend risk (5% weight)
        if 'attendance_trend' in df.columns:
            risk_score += np.where(df['attendance_trend'] < -10, 5, 0)
        
        # Convert score to categories
        df['dropout_risk_score'] = risk_score
        df['dropout_risk'] = pd.cut(risk_score, bins=[-1, 30, 60, 100], 
                                    labels=['Low Risk', 'Medium Risk', 'High Risk'])
        
        print(f"✅ Target variable created")
        print(f"\nRisk Distribution:")
        print(df['dropout_risk'].value_counts())
        
        return df


if __name__ == "__main__":
    loader = DataLoader(data_dir='dummy_data')
    master_df = loader.load_all_data()
    
    # Save processed data
    master_df.to_csv('processed_data.csv', index=False)
    print(f"\n💾 Saved processed data: processed_data.csv")
    print(f"Shape: {master_df.shape}")
    print(f"\nColumns: {list(master_df.columns)}")