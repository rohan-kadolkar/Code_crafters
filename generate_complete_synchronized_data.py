"""
COMPLETE SYNCHRONIZED DATA GENERATOR
Generates teachers first, then students assigned to them
Maintains real-world college structure
"""

import random
import pandas as pd
from datetime import timedelta, datetime
import json
import os


class CompleteSynchronizedDataGenerator:
    def __init__(self):
        self.start_date = datetime(2025, 8, 1)
        self.current_date = datetime(2025, 12, 1)
        
        # College structure - REALISTIC distribution
        self.branches = {
            'CS': {'name': 'Computer Science', 'students_per_year': [60, 55, 50, 45]},
            'EC': {'name': 'Electronics & Communication', 'students_per_year': [50, 48, 45, 40]},
            'ME': {'name': 'Mechanical Engineering', 'students_per_year': [45, 42, 40, 38]},
            'CE': {'name': 'Civil Engineering', 'students_per_year': [40, 38, 35, 32]},
            'EE': {'name': 'Electrical Engineering', 'students_per_year': [45, 42, 40, 35]}
        }
        
        # Names database
        self.first_names_male = [
            'Aarav', 'Vivaan', 'Aditya', 'Vihaan', 'Arjun', 'Sai', 'Arnav', 'Ayaan',
            'Krishna', 'Ishaan', 'Shaurya', 'Atharv', 'Advait', 'Pranav', 'Dhruv',
            'Aryan', 'Kabir', 'Shivansh', 'Rudra', 'Ritvik', 'Vedant', 'Reyansh',
            'Samar', 'Daksh', 'Kiaan', 'Ansh', 'Naksh', 'Yash', 'Kian', 'Raj',
            'Rohan', 'Amit', 'Rahul', 'Siddharth', 'Varun', 'Kunal', 'Nikhil',
            'Abhinav', 'Karthik', 'Ankit', 'Harshit', 'Manish', 'Prakash', 'Ravi',
            'Suresh', 'Manoj', 'Deepak', 'Sandeep', 'Vikram', 'Ajay'
        ]
        
        self.first_names_female = [
            'Saanvi', 'Aanya', 'Diya', 'Ananya', 'Pari', 'Aadhya', 'Kavya', 'Sara',
            'Myra', 'Aditi', 'Avni', 'Shanaya', 'Navya', 'Kiara', 'Riya', 'Aarohi',
            'Prisha', 'Anvi', 'Siya', 'Ishita', 'Anika', 'Tara', 'Zara', 'Mira',
            'Ira', 'Nisha', 'Sneha', 'Priya', 'Divya', 'Pooja', 'Anjali', 'Shruti',
            'Meera', 'Tanvi', 'Swati', 'Kriti', 'Simran', 'Neha', 'Ritika', 'Sakshi',
            'Preeti', 'Rani', 'Suman', 'Rekha', 'Sunita'
        ]
        
        self.last_names = [
            'Kumar', 'Singh', 'Sharma', 'Patel', 'Reddy', 'Gupta', 'Mehta', 'Joshi',
            'Desai', 'Agarwal', 'Verma', 'Shah', 'Iyer', 'Nair', 'Pillai', 'Rao',
            'Choudhury', 'Malhotra', 'Kapoor', 'Bose', 'Ghosh', 'Das', 'Chatterjee',
            'Banerjee', 'Mukherjee', 'Jain', 'Sinha', 'Pandey', 'Mishra', 'Tiwari',
            'Saxena', 'Arora', 'Bhatia', 'Khanna', 'Sethi', 'Chopra', 'Kaur', 'Khan',
            'Ali', 'Hussain', 'Ahmed'
        ]
        
        self.teacher_first_names = [
            'Rajesh', 'Priya', 'Amit', 'Sunita', 'Vijay', 'Rekha', 'Suresh', 'Kavita',
            'Ramesh', 'Anita', 'Manoj', 'Neha', 'Ashok', 'Pooja', 'Sanjay', 'Meera',
            'Deepak', 'Ritu', 'Anil', 'Shweta', 'Rakesh', 'Nisha', 'Vinod', 'Preeti',
            'Alok', 'Swati', 'Naveen', 'Divya', 'Ajay', 'Sonal'
        ]
        
        self.cities = [
            'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad', 'Chennai', 'Kolkata', 'Pune',
            'Ahmedabad', 'Jaipur', 'Lucknow', 'Kanpur', 'Nagpur', 'Indore', 'Bhopal',
            'Visakhapatnam', 'Patna', 'Vadodara', 'Ghaziabad', 'Ludhiana', 'Coimbatore'
        ]
        
        self.subjects = [
            'Mathematics', 'Physics', 'Chemistry', 'Computer Science',
            'Electronics', 'Mechanical Engineering', 'English', 'Data Structures'
        ]
        
        # Extracurricular activities
        self.clubs_activities = {
            'Technical': ['Coding Club', 'Robotics Club', 'AI/ML Club', 'Web Development Club'],
            'Sports': ['Cricket Team', 'Football Team', 'Basketball Team', 'Badminton Club'],
            'Cultural': ['Music Club', 'Dance Club', 'Drama Club', 'Photography Club'],
            'Social': ['NSS', 'NCC', 'Rotaract Club', 'Environmental Club'],
            'Academic': ['Quiz Club', 'Mathematics Club', 'Research Club', 'Innovation Club'],
            'Other': ['Student Council', 'Event Management Team', 'College Magazine']
        }
        
        print("="*80)
        print("🎓 COMPLETE SYNCHRONIZED DATA GENERATOR")
        print("="*80)
    
    def generate_all_data(self, output_dir='data/dummy_data'):
        """Master function to generate all data in correct order"""
        
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.dirname(output_dir), exist_ok=True)
        
        # STEP 1: Generate teachers (hierarchical structure)
        print("\n📚 STEP 1: Generating Teachers...")
        teachers_df = self.generate_teachers()
        teachers_df.to_csv(f'{output_dir}/teachers.csv', index=False)
        
        # STEP 2: Generate students assigned to teachers
        print("\n👨‍🎓 STEP 2: Generating Students...")
        students_df = self.generate_students(teachers_df)
        students_df.to_csv(f'{output_dir}/01_students_master.csv', index=False)
        
        # STEP 3: Generate supporting data
        print("\n👨‍👩‍👦 STEP 3: Generating Family Background...")
        family_df = self.generate_family_background(students_df)
        family_df.to_csv(f'{output_dir}/02_family_background.csv', index=False)
        
        print("\n📊 STEP 4: Generating Academic History...")
        academic_df = self.generate_academic_history(students_df)
        academic_df.to_csv(f'{output_dir}/03_academic_history.csv', index=False)
        
        print("\n📅 STEP 5: Generating Attendance...")
        attendance_df = self.generate_daily_attendance(students_df)
        attendance_df.to_csv(f'{output_dir}/04_daily_attendance.csv', index=False)
        
        print("\n📝 STEP 6: Generating Marks...")
        marks_df = self.generate_marks_data(students_df)
        marks_df.to_csv(f'{output_dir}/05_marks_exams.csv', index=False)
        
        print("\n📋 STEP 7: Generating Assignments...")
        assignments_df = self.generate_assignments(students_df)
        assignments_df.to_csv(f'{output_dir}/06_assignments.csv', index=False)
        
        print("\n📢 STEP 8: Generating Behavior Reports...")
        behavior_df = self.generate_behavior_reports(students_df)
        behavior_df.to_csv(f'{output_dir}/07_behavior_reports.csv', index=False)
        
        print("\n📚 STEP 9: Generating Library Usage...")
        library_df = self.generate_library_usage(students_df)
        library_df.to_csv(f'{output_dir}/08_library_usage.csv', index=False)
        
        print("\n💰 STEP 10: Generating Fee Payments...")
        fee_df = self.generate_fee_payments(students_df, family_df)
        fee_df.to_csv(f'{output_dir}/09_fee_payments.csv', index=False)
        
        print("\n🎯 STEP 11: Generating Extracurricular Activities...")
        extra_reg_df, extra_details_df, extra_attendance_df = self.generate_extracurricular(students_df)
        extra_reg_df.to_csv(f'{output_dir}/10_extracurricular_registrations.csv', index=False)
        extra_details_df.to_csv(f'{output_dir}/11_extracurricular_details.csv', index=False)
        extra_attendance_df.to_csv(f'{output_dir}/12_extracurricular_attendance.csv', index=False)
        
        # STEP 12: Generate teacher credentials and mappings
        print("\n🔐 STEP 12: Generating Teacher Credentials...")
        self.generate_teacher_credentials(teachers_df, students_df, output_dir)
        
        # Generate summary
        self.generate_summary_report(output_dir, teachers_df, students_df, family_df, academic_df,
                                    attendance_df, marks_df, assignments_df, behavior_df, 
                                    library_df, fee_df, extra_reg_df, extra_details_df, extra_attendance_df)
        
        print("\n" + "="*80)
        print("✅ COMPLETE DATA GENERATION SUCCESSFUL!")
        print("="*80)
        print(f"\n📁 Output Directory: {output_dir}")
        print(f"\n📊 Generated Files:")
        print(f"   - teachers.csv ({len(teachers_df)} teachers)")
        print(f"   - 01_students_master.csv ({len(students_df)} students)")
        print(f"   - 02-12: All supporting data files")
        print(f"   - teachers.json (login credentials)")
        print(f"   - student_teacher_mapping.json")
        
        return {
            'teachers': teachers_df,
            'students': students_df,
            'family': family_df,
            'academic': academic_df
        }
    
    def generate_teachers(self):
        """Generate teachers with hierarchical structure"""
        teachers = []
        teacher_id = 1
        
        for branch_code, branch_info in self.branches.items():
            branch_name = branch_info['name']
            
            for year in range(1, 5):  # Years 1-4
                # 1 Class Coordinator + 2-3 Subject Teachers per year
                num_teachers = 4  # Fixed: 1 coordinator + 3 teachers
                
                for i in range(num_teachers):
                    first_name = random.choice(self.teacher_first_names)
                    last_name = random.choice(self.last_names)
                    title = random.choice(['Prof.', 'Dr.', 'Mr.', 'Ms.'])
                    
                    # Assign role
                    if i == 0:
                        role = 'Class Coordinator'
                    elif i == 1:
                        role = 'Faculty Advisor'
                    else:
                        role = f'Subject Teacher {i-1}'
                    
                    # Assign subjects based on branch
                    if branch_code == 'CS':
                        subject_pool = ['Computer Science', 'Data Structures', 'Mathematics', 'Physics']
                    elif branch_code == 'EC':
                        subject_pool = ['Electronics', 'Physics', 'Mathematics', 'Computer Science']
                    elif branch_code == 'ME':
                        subject_pool = ['Mechanical Engineering', 'Physics', 'Mathematics', 'Chemistry']
                    elif branch_code == 'CE':
                        subject_pool = ['Civil Engineering', 'Physics', 'Mathematics', 'Chemistry']
                    else:  # EE
                        subject_pool = ['Electronics', 'Physics', 'Mathematics', 'Computer Science']
                    
                    teacher = {
                        'teacher_id': teacher_id,
                        'name': f"{title} {first_name} {last_name}",
                        'first_name': first_name,
                        'last_name': last_name,
                        'title': title,
                        'email': f"{first_name.lower()}.{last_name.lower()}@college.edu",
                        'username': f"teacher{teacher_id}",
                        'password': f"pass{teacher_id}",
                        'phone': f"+91{random.randint(7000000000, 9999999999)}",
                        'branch': branch_code,
                        'branch_name': branch_name,
                        'year': year,
                        'role': role,
                        'subjects': ','.join(random.sample(subject_pool, k=min(2, len(subject_pool)))),
                        'experience_years': random.randint(3, 20),
                        'qualification': random.choice(['M.Tech', 'Ph.D.', 'M.Sc.', 'M.E.', 'B.Tech']),
                        'joining_date': (self.start_date - timedelta(days=random.randint(365, 3650))).strftime('%Y-%m-%d'),
                        'is_hod': False
                    }
                    
                    teachers.append(teacher)
                    teacher_id += 1
        
        # Mark one teacher per branch as HOD
        df = pd.DataFrame(teachers)
        for branch in self.branches.keys():
            branch_teachers = df[df['branch'] == branch]
            if len(branch_teachers) > 0:
                hod_idx = branch_teachers.index[0]
                df.at[hod_idx, 'is_hod'] = True
                df.at[hod_idx, 'role'] = 'HOD & Class Coordinator'
        
        print(f"✅ Generated {len(df)} teachers across all branches and years")
        return df
    
    def generate_students(self, teachers_df):
        """Generate students and assign to teachers"""
        students = []
        student_id = 1
        
        for branch_code, branch_info in self.branches.items():
            for year_idx, num_students in enumerate(branch_info['students_per_year']):
                year = year_idx + 1
                
                # Get class coordinator for this branch and year
                coordinator = teachers_df[
                    (teachers_df['branch'] == branch_code) & 
                    (teachers_df['year'] == year) &
                    (teachers_df['role'].str.contains('Coordinator'))
                ]
                
                if len(coordinator) == 0:
                    print(f"⚠️ No coordinator found for {branch_code} Year {year}")
                    continue
                
                coordinator_id = coordinator.iloc[0]['teacher_id']
                coordinator_name = coordinator.iloc[0]['name']
                
                # Distribute students across semesters
                sem1_count = num_students // 2
                sem2_count = num_students - sem1_count
                
                for semester in [1, 2]:
                    count = sem1_count if semester == 1 else sem2_count
                    
                    for i in range(count):
                        gender = random.choice(['Male', 'Female'])
                        first_name = random.choice(
                            self.first_names_male if gender == 'Male' else self.first_names_female
                        )
                        last_name = random.choice(self.last_names)
                        
                        roll_number = f"{branch_code}{20+year}{semester}{i+1:03d}"
                        
                        student = {
                            'student_id': student_id,
                            'roll_number': roll_number,
                            'first_name': first_name,
                            'last_name': last_name,
                            'full_name': f"{first_name} {last_name}",
                            'gender': gender,
                            'age': 17 + year - 1 + random.randint(0, 2),
                            'date_of_birth': (datetime(2007 - year + 1, 1, 1) + timedelta(days=random.randint(0, 365))).strftime('%Y-%m-%d'),
                            'email': f"{first_name.lower()}.{last_name.lower()}{student_id}@student.college.edu",
                            'phone': f"+91{random.randint(7000000000, 9999999999)}",
                            'city': random.choice(self.cities),
                            'location_type': random.choices(['Rural', 'Semi-Urban', 'Urban'], 
                                                           weights=[0.40, 0.35, 0.25], k=1)[0],
                            'branch': branch_code,
                            'branch_name': branch_info['name'],
                            'year': year,
                            'semester': semester,
                            'admission_date': self.start_date.strftime('%Y-%m-%d'),
                            'status': 'Active',
                            'primary_teacher_id': int(coordinator_id),
                            'class_coordinator': coordinator_name
                        }
                        
                        students.append(student)
                        student_id += 1
        
        print(f"✅ Generated {len(students)} students assigned to teachers")
        return pd.DataFrame(students)
    
    def generate_family_background(self, students_df):
        """Generate family background data"""
        family_data = []

        for _, student in students_df.iterrows():
            if student['location_type'] == 'Rural':
                income_level = random.choices(['Low', 'Lower-Middle', 'Middle'], weights=[0.60, 0.30, 0.10], k=1)[0]
            elif student['location_type'] == 'Semi-Urban':
                income_level = random.choices(['Low', 'Lower-Middle', 'Middle', 'Upper-Middle'],
                                           weights=[0.25, 0.35, 0.30, 0.10], k=1)[0]
            else:  # Urban
                income_level = random.choices(['Lower-Middle', 'Middle', 'Upper-Middle', 'High'],
                                           weights=[0.20, 0.40, 0.30, 0.10], k=1)[0]

            parent_education_options = ['No Formal Education', 'Primary', 'Secondary',
                                      'Higher Secondary', 'Graduate', 'Post-Graduate']

            father_education = random.choices(parent_education_options,
                                           weights=[0.15, 0.20, 0.25, 0.20, 0.15, 0.05], k=1)[0]
            mother_education = random.choices(parent_education_options,
                                           weights=[0.20, 0.25, 0.25, 0.15, 0.10, 0.05], k=1)[0]

            occupations = ['Farmer', 'Daily Wage Worker', 'Small Business', 'Salaried Employee',
                          'Government Employee', 'Professional', 'Retired', 'Self-Employed']

            father_occupation = random.choice(occupations)
            mother_occupation = random.choices(occupations + ['Homemaker'],
                                            weights=[0.05, 0.05, 0.10, 0.10, 0.08, 0.05, 0.02, 0.10, 0.45], k=1)[0]

            siblings = random.choices([0, 1, 2, 3, 4], weights=[0.15, 0.35, 0.30, 0.15, 0.05], k=1)[0]
            single_parent = random.choices([0, 1], weights=[0.92, 0.08], k=1)[0]

            income_ranges = {
                'Low': random.randint(50000, 150000),
                'Lower-Middle': random.randint(150000, 300000),
                'Middle': random.randint(300000, 600000),
                'Upper-Middle': random.randint(600000, 1000000),
                'High': random.randint(1000000, 3000000)
            }

            family = {
                'student_id': student['student_id'],
                'income_level': income_level,
                'annual_income': income_ranges[income_level],
                'father_name': f"Mr. {random.choice(self.first_names_male)} {student['last_name']}",
                'father_education': father_education,
                'father_occupation': father_occupation,
                'mother_name': f"Mrs. {random.choice(self.first_names_female)} {student['last_name']}",
                'mother_education': mother_education,
                'mother_occupation': mother_occupation,
                'siblings': siblings,
                'family_size': random.randint(3, 7),
                'single_parent': single_parent,
                'guardian_contact': f"+91{random.randint(7000000000, 9999999999)}",
                'permanent_address': f"{random.randint(1, 500)}, {random.choice(['Street', 'Road', 'Lane'])}, {student['city']}"
            }
            family_data.append(family)

        df = pd.DataFrame(family_data)
        print(f"✅ Generated family background for {len(df)} students")
        return df
    
    def generate_academic_history(self, students_df):
        """Generate academic history"""
        academic_records = []

        for _, student in students_df.iterrows():
            current_year = student['year']
            current_semester = student['semester']
            
            semesters_completed = (current_year - 1) * 2 + (current_semester - 1)
            
            performance_trend = random.choices(
                ['Declining', 'Stable', 'Improving'], 
                weights=[0.25, 0.50, 0.25], 
                k=1
            )[0]
            
            # GPA Calculation
            if semesters_completed > 0:
                if performance_trend == 'Declining':
                    base_gpa = random.uniform(4.0, 7.0)
                    previous_gpa = base_gpa + random.uniform(0.5, 1.5)
                elif performance_trend == 'Improving':
                    base_gpa = random.uniform(6.0, 9.0)
                    previous_gpa = base_gpa - random.uniform(0.5, 1.5)
                else:
                    base_gpa = random.uniform(5.0, 8.5)
                    previous_gpa = base_gpa + random.uniform(-0.3, 0.3)
                
                current_semester_gpa = round(base_gpa, 2)
                previous_semester_gpa = round(max(0, min(10, previous_gpa)), 2)
            else:
                entrance_percentile = random.uniform(40, 98)
                current_semester_gpa = round((entrance_percentile / 10) * random.uniform(0.8, 1.1), 2)
                previous_semester_gpa = None
            
            if semesters_completed > 0:
                cumulative_gpa = round(
                    (previous_semester_gpa * 0.6 + current_semester_gpa * 0.4) 
                    if previous_semester_gpa else current_semester_gpa,
                    2
                )
            else:
                cumulative_gpa = current_semester_gpa
            
            # Credit Hours
            credits_registered_this_sem = random.choice([18, 20, 22, 24])
            
            if cumulative_gpa >= 8.0:
                completion_rate = random.uniform(0.95, 1.0)
            elif cumulative_gpa >= 6.0:
                completion_rate = random.uniform(0.80, 0.95)
            elif cumulative_gpa >= 4.0:
                completion_rate = random.uniform(0.60, 0.85)
            else:
                completion_rate = random.uniform(0.40, 0.70)
            
            credits_completed_this_sem = int(credits_registered_this_sem * completion_rate)
            
            total_credits_registered = credits_registered_this_sem * (semesters_completed + 1)
            total_credits_completed = int(total_credits_registered * completion_rate)
            
            credit_completion_rate = round((total_credits_completed / total_credits_registered * 100), 2)
            
            # First Year Performance
            if current_year == 1:
                first_year_gpa = current_semester_gpa
                first_year_credits_completed = credits_completed_this_sem
                first_year_attendance = random.uniform(60, 95)
                first_year_dropout_risk = 'High' if first_year_gpa < 5.0 else 'Medium' if first_year_gpa < 7.0 else 'Low'
            else:
                first_year_gpa = round(cumulative_gpa + random.uniform(-1.0, 0.5), 2)
                first_year_credits_completed = random.choice([36, 38, 40, 42, 44])
                first_year_attendance = random.uniform(65, 95)
                first_year_dropout_risk = 'Low'
            
            # Registration Delays
            expected_registration_date = self.start_date - timedelta(days=5)
            
            registration_delay_days = random.choices(
                [0, 1, 2, 3, 5, 7, 10, 15, 20],
                weights=[0.50, 0.15, 0.10, 0.08, 0.07, 0.05, 0.03, 0.01, 0.01],
                k=1
            )[0]
            
            actual_registration_date = expected_registration_date + timedelta(days=registration_delay_days)
            registration_status = 'On Time' if registration_delay_days <= 2 else 'Late' if registration_delay_days <= 7 else 'Very Late'
            
            # Withdrawals
            if semesters_completed > 0:
                if cumulative_gpa < 5.0:
                    courses_withdrawn_ever = random.choices([0, 1, 2, 3], weights=[0.30, 0.40, 0.20, 0.10], k=1)[0]
                elif cumulative_gpa < 7.0:
                    courses_withdrawn_ever = random.choices([0, 1, 2], weights=[0.60, 0.30, 0.10], k=1)[0]
                else:
                    courses_withdrawn_ever = random.choices([0, 1], weights=[0.85, 0.15], k=1)[0]
            else:
                courses_withdrawn_ever = 0
            
            courses_withdrawn_current = 1 if random.random() < 0.05 else 0
            total_withdrawals = courses_withdrawn_ever + courses_withdrawn_current
            
            semester_number = semesters_completed + 1
            
            # Course failures
            if cumulative_gpa < 5.0:
                courses_failed = random.choices([0, 1, 2, 3, 4], weights=[0.10, 0.30, 0.30, 0.20, 0.10], k=1)[0]
            elif cumulative_gpa < 7.0:
                courses_failed = random.choices([0, 1, 2], weights=[0.50, 0.35, 0.15], k=1)[0]
            else:
                courses_failed = random.choices([0, 1], weights=[0.90, 0.10], k=1)[0]
            
            courses_repeated = min(courses_failed, random.randint(0, 2))
            
            academic_record = {
                'student_id': student['student_id'],
                'current_semester_gpa': current_semester_gpa,
                'previous_semester_gpa': previous_semester_gpa,
                'cumulative_gpa': cumulative_gpa,
                'gpa_trend': performance_trend,
                'credits_registered_current': credits_registered_this_sem,
                'credits_completed_current': credits_completed_this_sem,
                'total_credits_registered': total_credits_registered,
                'total_credits_completed': total_credits_completed,
                'credit_completion_rate': credit_completion_rate,
                'first_year_gpa': round(first_year_gpa, 2),
                'first_year_credits_completed': first_year_credits_completed,
                'first_year_attendance_percent': round(first_year_attendance, 2),
                'first_year_dropout_risk': first_year_dropout_risk,
                'registration_date': actual_registration_date.strftime('%Y-%m-%d'),
                'registration_delay_days': registration_delay_days,
                'registration_status': registration_status,
                'courses_withdrawn_ever': courses_withdrawn_ever,
                'courses_withdrawn_current': courses_withdrawn_current,
                'total_course_withdrawals': total_withdrawals,
                'semester_number': semester_number,
                'courses_failed_ever': courses_failed,
                'courses_repeated': courses_repeated,
                'academic_standing': self._calculate_academic_standing(cumulative_gpa),
                'probation_status': 'Yes' if cumulative_gpa < 5.0 else 'No'
            }
            
            academic_records.append(academic_record)

        df = pd.DataFrame(academic_records)
        print(f"✅ Generated academic history for {len(df)} students")
        return df
    
    def _calculate_academic_standing(self, gpa):
        """Calculate academic standing"""
        if gpa >= 8.5:
            return 'Excellent'
        elif gpa >= 7.0:
            return 'Good'
        elif gpa >= 5.5:
            return 'Average'
        elif gpa >= 4.0:
            return 'Below Average'
        else:
            return 'Poor'
    
    def generate_daily_attendance(self, students_df):
        """Generate daily attendance for past 8 weeks"""
        attendance_records = []
        weeks = 8

        for _, student in students_df.iterrows():
            base_rate = random.uniform(0.65, 0.95)
            current_date_iter = self.current_date - timedelta(weeks=weeks)

            for week in range(weeks):
                for day in range(5):
                    date = current_date_iter + timedelta(days=week*7 + day)
                    if date > self.current_date:
                        continue

                    day_name = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'][day]
                    if day == 0: prob = base_rate * 0.85
                    elif day == 4: prob = base_rate * 0.90
                    else: prob = base_rate

                    if random.random() < 0.25:
                        prob -= (week / weeks) * 0.2

                    status = 'Present' if random.random() < prob else 'Absent'

                    record = {
                        'student_id': student['student_id'],
                        'date': date.strftime('%Y-%m-%d'),
                        'day_of_week': day_name,
                        'week_number': week + 1,
                        'status': status,
                        'marked_by': student['class_coordinator'],
                        'marked_at': date.strftime('%Y-%m-%d %H:%M:%S')
                    }
                    attendance_records.append(record)

        df = pd.DataFrame(attendance_records)
        print(f"✅ Generated {len(df)} attendance records")
        return df
    
    def generate_marks_data(self, students_df):
        """Generate marks for exams"""
        marks_records = []
        exam_types = [
            ('Unit Test 1', 20, '2025-09-15'),
            ('Unit Test 2', 20, '2025-10-20'),
            ('Mid Semester', 30, '2025-11-10'),
            ('Assignment 1', 10, '2025-09-30'),
            ('Assignment 2', 10, '2025-10-30'),
            ('Lab Internal', 10, '2025-11-20')
        ]

        for _, student in students_df.iterrows():
            aptitude = random.uniform(40, 95)
            for subject in self.subjects[:6]:
                for exam_name, max_marks, exam_date in exam_types:
                    performance_factor = random.uniform(0.7, 1.1)
                    obtained = aptitude * (max_marks / 100) * performance_factor
                    obtained = max(0, min(max_marks, obtained + random.uniform(-3, 3)))
                    
                    if random.random() < 0.20:
                        if 'Test 2' in exam_name or 'Mid' in exam_name:
                            obtained *= 0.75

                    record = {
                        'student_id': student['student_id'],
                        'subject': subject,
                        'exam_type': exam_name,
                        'max_marks': max_marks,
                        'obtained_marks': round(obtained, 2),
                        'percentage': round((obtained / max_marks) * 100, 2),
                        'exam_date': exam_date,
                        'evaluator': student['class_coordinator']
                    }
                    marks_records.append(record)

        df = pd.DataFrame(marks_records)
        print(f"✅ Generated {len(df)} marks records")
        return df
    
    def generate_assignments(self, students_df):
        """Generate assignment submissions"""
        assignment_records = []
        assignments = [
            ('Assignment 1 - Subject A', '2025-09-15', '2025-09-30'),
            ('Assignment 2 - Subject B', '2025-10-01', '2025-10-15'),
            ('Assignment 3 - Subject C', '2025-10-20', '2025-11-05'),
            ('Assignment 4 - Subject D', '2025-11-10', '2025-11-25'),
            ('Project Proposal', '2025-09-20', '2025-10-10'),
            ('Lab Report 1', '2025-10-05', '2025-10-20'),
            ('Lab Report 2', '2025-11-01', '2025-11-15'),
            ('Case Study', '2025-11-15', '2025-11-30')
        ]

        for _, student in students_df.iterrows():
            for assignment_name, assigned_date, due_date in assignments:
                submit_prob = random.uniform(0.60, 0.95)
                submitted = random.random() < submit_prob

                if submitted:
                    due_dt = datetime.strptime(due_date, '%Y-%m-%d')
                    if random.random() < 0.75:
                        submit_date = due_dt - timedelta(days=random.randint(0, 3))
                    else:
                        submit_date = due_dt + timedelta(days=random.randint(1, 7))

                    submitted_on = submit_date.strftime('%Y-%m-%d')
                    status = 'On Time' if submit_date <= due_dt else 'Late'
                    grade = random.choices(['A', 'B', 'C', 'D'], weights=[0.30, 0.40, 0.20, 0.10], k=1)[0]
                else:
                    submitted_on = None
                    status = 'Not Submitted'
                    grade = None

                record = {
                    'student_id': student['student_id'],
                    'assignment_name': assignment_name,
                    'assigned_date': assigned_date,
                    'due_date': due_date,
                    'submitted': 'Yes' if submitted else 'No',
                    'submission_date': submitted_on,
                    'status': status,
                    'grade': grade,
                    'feedback': 'Good work' if grade in ['A', 'B'] else 'Needs improvement' if grade else None
                }
                assignment_records.append(record)

        df = pd.DataFrame(assignment_records)
        print(f"✅ Generated {len(df)} assignment records")
        return df
    
    def generate_behavior_reports(self, students_df):
        """Generate behavior reports"""
        behavior_records = []
        behaviors = [
            ('Excellent Participation', 'Positive', 'Always participates actively in class'),
            ('Punctual', 'Positive', 'Always on time for classes'),
            ('Helpful to Peers', 'Positive', 'Assists other students'),
            ('Late to Class', 'Negative', 'Frequently arrives late'),
            ('Irregular Attendance', 'Negative', 'Missing classes without notice'),
            ('Distracted in Class', 'Negative', 'Not paying attention'),
            ('Good Team Player', 'Positive', 'Works well in groups'),
            ('Respectful Behavior', 'Positive', 'Shows respect to faculty and peers')
        ]

        students_with_reports = students_df.sample(frac=0.30)

        for _, student in students_with_reports.iterrows():
            num_reports = random.randint(1, 3)
            for _ in range(num_reports):
                behavior, type_, description = random.choice(behaviors)
                report_date = (self.current_date - timedelta(days=random.randint(1, 90))).strftime('%Y-%m-%d')

                record = {
                    'student_id': student['student_id'],
                    'report_date': report_date,
                    'behavior_type': type_,
                    'behavior': behavior,
                    'description': description,
                    'reported_by': student['class_coordinator'],
                    'severity': random.choice(['Low', 'Medium', 'High']) if type_ == 'Negative' else 'Positive'
                }
                behavior_records.append(record)

        df = pd.DataFrame(behavior_records)
        print(f"✅ Generated {len(df)} behavior reports")
        return df
    
    def generate_library_usage(self, students_df):
        """Generate library usage"""
        library_records = []
        books = [
            'Introduction to Algorithms', 'Data Structures and Algorithms',
            'Computer Networks', 'Operating Systems', 'Database Management Systems',
            'Software Engineering', 'Artificial Intelligence', 'Machine Learning',
            'Physics Vol 1', 'Chemistry Fundamentals', 'Advanced Mathematics',
            'Digital Electronics', 'Control Systems', 'Power Systems'
        ]

        active_library_users = students_df.sample(frac=0.60)

        for _, student in active_library_users.iterrows():
            num_visits = random.randint(5, 20)
            for _ in range(num_visits):
                visit_date = (self.current_date - timedelta(days=random.randint(1, 100))).strftime('%Y-%m-%d')
                activity = random.choice(['Book Borrowed', 'Reading Session', 'Book Returned'])
                
                record = {
                    'student_id': student['student_id'],
                    'visit_date': visit_date,
                    'activity': activity,
                    'book_title': random.choice(books) if 'Book' in activity else None,
                    'duration_hours': random.randint(1, 4) if activity == 'Reading Session' else None,
                    'checkout_date': visit_date if activity == 'Book Borrowed' else None,
                    'return_date': (datetime.strptime(visit_date, '%Y-%m-%d') + timedelta(days=random.randint(7, 21))).strftime('%Y-%m-%d') if activity == 'Book Returned' else None
                }
                library_records.append(record)

        df = pd.DataFrame(library_records)
        print(f"✅ Generated {len(df)} library usage records")
        return df
    
    def generate_fee_payments(self, students_df, family_df):
        """Generate fee payments"""
        fee_records = []
        merged = students_df.merge(family_df[['student_id', 'income_level']], on='student_id')

        installments = [
            ('Semester 1 - Tuition', 35000, '2025-08-15'),
            ('Semester 1 - Other', 15000, '2025-08-15'),
            ('Semester 2 - Tuition', 35000, '2025-01-15'),
            ('Semester 2 - Other', 15000, '2025-01-15')
        ]

        for _, student in merged.iterrows():
            if student['income_level'] == 'Low':
                payment_prob, delay_prob = 0.60, 0.50
            elif student['income_level'] in ['Lower-Middle', 'Middle']:
                payment_prob, delay_prob = 0.85, 0.30
            else:
                payment_prob, delay_prob = 0.98, 0.10

            for installment_name, amount, due_date in installments:
                due_dt = datetime.strptime(due_date, '%Y-%m-%d')
                if due_dt > self.current_date:
                    continue

                paid = random.random() < payment_prob
                if paid:
                    if random.random() < delay_prob:
                        payment_date = due_dt + timedelta(days=random.randint(10, 60))
                    else:
                        payment_date = due_dt - timedelta(days=random.randint(0, 10))
                    
                    status = 'Paid - On Time' if payment_date <= due_dt else 'Paid - Late'
                    paid_amount = amount
                else:
                    payment_date = None
                    status = 'Pending'
                    paid_amount = 0

                record = {
                    'student_id': student['student_id'],
                    'installment': installment_name,
                    'amount_due': amount,
                    'due_date': due_date,
                    'payment_date': payment_date.strftime('%Y-%m-%d') if payment_date else None,
                    'amount_paid': paid_amount,
                    'status': status,
                    'payment_method': random.choice(['Online', 'Cheque', 'Cash', 'DD']) if paid else None,
                    'receipt_number': f"RCP{random.randint(10000, 99999)}" if paid else None
                }
                fee_records.append(record)

        df = pd.DataFrame(fee_records)
        print(f"✅ Generated {len(df)} fee payment records")
        return df
    
    def generate_extracurricular(self, students_df):
        """Generate extracurricular activities"""
        
        # Registrations
        reg_records = []
        detail_records = []
        attendance_records = []
        
        for _, student in students_df.iterrows():
            participates = random.random() < 0.65
            
            if not participates:
                reg_records.append({
                    'student_id': student['student_id'],
                    'total_activities': 0,
                    'participation_status': 'Not Participating',
                    'registration_date': None
                })
                continue
            
            num_activities = random.choices([1, 2, 3, 4], weights=[0.40, 0.35, 0.20, 0.05], k=1)[0]
            
            selected_categories = random.sample(list(self.clubs_activities.keys()), 
                                               k=min(num_activities, len(self.clubs_activities)))
            
            activities_joined = []
            for category in selected_categories:
                activity = random.choice(self.clubs_activities[category])
                
                reg_days_after_start = random.randint(1, 30)
                registration_date = self.start_date + timedelta(days=reg_days_after_start)
                
                role = random.choices(
                    ['Member', 'Active Member', 'Core Team', 'Coordinator', 'President/Head'],
                    weights=[0.60, 0.25, 0.10, 0.03, 0.02],
                    k=1
                )[0]
                
                if role in ['President/Head', 'Coordinator']:
                    activity_level = 'Very High'
                elif role == 'Core Team':
                    activity_level = random.choice(['High', 'Very High'])
                elif role == 'Active Member':
                    activity_level = random.choice(['Medium', 'High'])
                else:
                    activity_level = random.choices(['Low', 'Medium', 'High'], 
                                                   weights=[0.40, 0.40, 0.20], k=1)[0]
                
                hours_per_week = {
                    'Low': random.randint(1, 3),
                    'Medium': random.randint(3, 6),
                    'High': random.randint(6, 10),
                    'Very High': random.randint(10, 15)
                }[activity_level]
                
                events_participated = {
                    'Low': random.randint(0, 2),
                    'Medium': random.randint(2, 5),
                    'High': random.randint(5, 10),
                    'Very High': random.randint(10, 20)
                }[activity_level]
                
                has_achievement = random.choices([True, False], weights=[0.25, 0.75], k=1)[0]
                achievement = random.choice([
                    'Winner - Intra College Competition',
                    'Winner - Inter College Competition',
                    'Best Performer Award',
                    'Certificate of Excellence',
                    'Participation Certificate',
                    None
                ]) if has_achievement else None
                
                status = random.choices(['Active', 'Inactive'], weights=[0.85, 0.15], k=1)[0]
                
                detail_records.append({
                    'student_id': student['student_id'],
                    'activity_name': activity,
                    'activity_category': category,
                    'registration_date': registration_date.strftime('%Y-%m-%d'),
                    'role': role,
                    'activity_level': activity_level,
                    'hours_per_week': hours_per_week,
                    'total_events_participated': events_participated,
                    'achievement': achievement,
                    'status': status,
                    'faculty_coordinator': student['class_coordinator']
                })
                
                activities_joined.append({
                    'activity': activity,
                    'registration_date': registration_date.strftime('%Y-%m-%d')
                })
                
                # Generate attendance for this activity
                if status == 'Active':
                    if category in ['Technical', 'Academic']:
                        sessions_per_month = 4
                    elif category == 'Sports':
                        sessions_per_month = 14
                    elif category == 'Cultural':
                        sessions_per_month = 6
                    else:
                        sessions_per_month = 4
                    
                    months = 4
                    for month in range(months):
                        for session in range(sessions_per_month):
                            days_offset = (month * 30) + random.randint(0, 30)
                            session_date = self.start_date + timedelta(days=days_offset)
                            
                            if session_date > self.current_date:
                                continue
                            
                            attendance_prob = {
                                'Low': 0.50,
                                'Medium': 0.70,
                                'High': 0.85,
                                'Very High': 0.95
                            }[activity_level]
                            
                            attended = random.random() < attendance_prob
                            
                            session_type = random.choice([
                                'Regular Meeting', 'Practice Session', 'Workshop',
                                'Event', 'Competition', 'Training', 'Project Work'
                            ])
                            
                            duration_hours = random.choice([1, 1.5, 2, 2.5, 3, 4])
                            
                            attendance_records.append({
                                'student_id': student['student_id'],
                                'activity_name': activity,
                                'session_date': session_date.strftime('%Y-%m-%d'),
                                'session_type': session_type,
                                'session_time': f"{random.randint(14, 18):02d}:00:00",
                                'duration_hours': duration_hours,
                                'attendance_status': 'Present' if attended else 'Absent',
                                'marked_by': student['class_coordinator']
                            })
            
            reg_records.append({
                'student_id': student['student_id'],
                'total_activities': num_activities,
                'participation_status': 'Active',
                'registration_date': min([a['registration_date'] for a in activities_joined])
            })
        
        reg_df = pd.DataFrame(reg_records)
        detail_df = pd.DataFrame(detail_records)
        attendance_df = pd.DataFrame(attendance_records)
        
        print(f"✅ Generated {len(reg_df)} extracurricular registrations")
        print(f"✅ Generated {len(detail_df)} extracurricular details")
        print(f"✅ Generated {len(attendance_df)} extracurricular attendance records")
        
        return reg_df, detail_df, attendance_df
    
    def generate_teacher_credentials(self, teachers_df, students_df, output_dir):
        """Generate teacher credentials and student mappings"""
        
        # Teacher credentials for login
        teachers_list = []
        for _, teacher in teachers_df.iterrows():
            teachers_list.append({
                'teacher_id': int(teacher['teacher_id']),
                'name': teacher['name'],
                'email': teacher['email'],
                'username': teacher['username'],
                'password': teacher['password'],
                'branch': teacher['branch'],
                'branch_name': teacher['branch_name'],
                'year': int(teacher['year']),
                'role': teacher['role'],
                'subjects': teacher['subjects'].split(',') if isinstance(teacher['subjects'], str) else teacher['subjects']
            })
        
        parent_dir = os.path.dirname(output_dir)
        with open(f'{parent_dir}/teachers.json', 'w') as f:
            json.dump(teachers_list, f, indent=2)
        
        # Student-Teacher mapping
        mappings = []
        for _, student in students_df.iterrows():
            mappings.append({
                'teacher_id': int(student['primary_teacher_id']),
                'student_id': int(student['student_id'])
            })
        
        with open(f'{parent_dir}/student_teacher_mapping.json', 'w') as f:
            json.dump(mappings, f, indent=2)
        
        print(f"✅ Generated credentials for {len(teachers_list)} teachers")
        print(f"✅ Generated {len(mappings)} student-teacher mappings")
    
    def generate_summary_report(self, output_dir, teachers_df, students_df, family_df, academic_df,
                                attendance_df, marks_df, assignments_df, behavior_df, 
                                library_df, fee_df, extra_reg_df, extra_details_df, extra_attendance_df):
        """Generate comprehensive summary"""
        
        attendance_grouped = attendance_df.groupby('student_id')['status'].apply(
            lambda x: (x == 'Present').sum() / len(x) * 100
        )
        avg_attendance = attendance_grouped.mean()

        marks_grouped = marks_df.groupby('student_id')['percentage'].mean()
        avg_marks = marks_grouped.mean()

        assignments_grouped = assignments_df.groupby('student_id')['submitted'].apply(
            lambda x: (x == 'Yes').sum() / len(x) * 100
        )
        avg_assignment_completion = assignments_grouped.mean()

        fee_grouped = fee_df.groupby('student_id')['amount_paid'].sum()
        total_fee_collected = fee_grouped.sum()
        
        summary = f"""
{'='*80}
SYNCHRONIZED DATA GENERATION SUMMARY
{'='*80}

Generation Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## TEACHERS
Total Teachers: {len(teachers_df)}

By Branch:
{teachers_df.groupby('branch')['teacher_id'].count().to_string()}

By Role:
{teachers_df.groupby('role')['teacher_id'].count().to_string()}

## STUDENTS
Total Students: {len(students_df)}

By Branch:
{students_df.groupby('branch')['student_id'].count().to_string()}

By Year:
{students_df.groupby('year')['student_id'].count().to_string()}

## FAMILY BACKGROUND

Income Level Distribution:
- Low: {(family_df['income_level'] == 'Low').sum()}
- Lower-Middle: {(family_df['income_level'] == 'Lower-Middle').sum()}
- Middle: {(family_df['income_level'] == 'Middle').sum()}
- Upper-Middle: {(family_df['income_level'] == 'Upper-Middle').sum()}
- High: {(family_df['income_level'] == 'High').sum()}

## ACADEMIC HISTORY

Average Cumulative GPA: {academic_df['cumulative_gpa'].mean():.2f}
Average Credit Completion Rate: {academic_df['credit_completion_rate'].mean():.2f}%

Students on Academic Probation: {(academic_df['probation_status'] == 'Yes').sum()}
Students with Course Withdrawals: {(academic_df['total_course_withdrawals'] > 0).sum()}

## ATTENDANCE (CLASS)

Total Attendance Records: {len(attendance_df)}
Average Attendance: {avg_attendance:.2f}%
Students with <75% Attendance: {(attendance_grouped < 75).sum()}

## MARKS & EXAMS

Total Marks Records: {len(marks_df)}
Average Marks: {avg_marks:.2f}%

## ASSIGNMENTS

Total Assignment Records: {len(assignments_df)}
Average Completion Rate: {avg_assignment_completion:.2f}%

## BEHAVIOR REPORTS

Total Behavior Reports: {len(behavior_df)}
Positive Reports: {(behavior_df['behavior_type'] == 'Positive').sum()}
Negative Reports: {(behavior_df['behavior_type'] == 'Negative').sum()}

## LIBRARY USAGE

Total Library Records: {len(library_df)}
Active Library Users: {library_df['student_id'].nunique()}

## FEE PAYMENTS

Total Fee Records: {len(fee_df)}
Total Fee Collected: ₹{total_fee_collected:,.2f}

## EXTRACURRICULAR ACTIVITIES

Total Students Participating: {(extra_reg_df['participation_status'] == 'Active').sum()}
Participation Rate: {(extra_reg_df['participation_status'] == 'Active').sum() / len(students_df) * 100:.1f}%
Total Activity Registrations: {len(extra_details_df)}
Total Attendance Records: {len(extra_attendance_df)}

## SAMPLE TEACHER CREDENTIALS
{'='*60}
"""
        
        for i in range(min(10, len(teachers_df))):
            teacher = teachers_df.iloc[i]
            summary += f"\nUsername: {teacher['username']}\n"
            summary += f"Password: {teacher['password']}\n"
            summary += f"Name: {teacher['name']}\n"
            summary += f"Branch: {teacher['branch_name']} - Year {teacher['year']}\n"
            summary += f"Role: {teacher['role']}\n"
            
            # Count students for this teacher
            student_count = len(students_df[students_df['primary_teacher_id'] == teacher['teacher_id']])
            summary += f"Students: {student_count}\n"
            summary += f"{'-'*60}\n"
        
        summary += f"\n{'='*80}\n"
        summary += "✅ ALL DATA FULLY SYNCHRONIZED!\n"
        summary += "✅ Teachers created first, students assigned accordingly\n"
        summary += "✅ Real-world college structure maintained\n"
        summary += f"{'='*80}\n"
        
        with open(f'{output_dir}/00_data_summary.txt', 'w', encoding='utf-8') as f:
            f.write(summary)
        
        print("\n" + summary)


if __name__ == "__main__":
    generator = CompleteSynchronizedDataGenerator()
    generator.generate_all_data()
    
    print("\n🎉 SUCCESS! Run the ML pipeline next:")
    print("   python src/run_complete_pipeline.py")