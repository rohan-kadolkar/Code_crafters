"""
Generate realistic teacher data and assign students to teachers
"""

import pandas as pd
import json
import random


def generate_teacher_data():
    """Generate teacher data with credentials"""
    
    # Read student data to understand structure
    students_df = pd.read_csv('data/dummy_data/01_students_master.csv')
    
    # Branch -> Teachers mapping
    branches = {
        'CS': 'Computer Science',
        'EC': 'Electronics & Communication',
        'ME': 'Mechanical Engineering',
        'CE': 'Civil Engineering',
        'EE': 'Electrical Engineering'
    }
    
    teachers = []
    teacher_id = 1
    
    # Create teachers for each branch and year combination
    for branch_code, branch_name in branches.items():
        # Count students in this branch
        branch_students = students_df[students_df['branch'] == branch_code]
        
        for year in [1, 2, 3, 4]:
            year_students = branch_students[branch_students['year'] == year]
            
            if len(year_students) == 0:
                continue
            
            # 2-3 teachers per year per branch
            num_teachers = random.choice([2, 3])
            
            for i in range(num_teachers):
                teacher_name = f"{random.choice(['Prof.', 'Dr.', 'Mr.', 'Ms.'])} {random.choice(['Kumar', 'Sharma', 'Patel', 'Singh', 'Reddy', 'Gupta'])} {random.choice(['A', 'B', 'C', 'D', 'K', 'M', 'R', 'S'])}"
                
                teacher = {
                    'teacher_id': teacher_id,
                    'name': teacher_name,
                    'email': f"teacher{teacher_id}@college.edu",
                    'username': f"teacher{teacher_id}",
                    'password': f"pass{teacher_id}",  # In production, hash this!
                    'branch': branch_code,
                    'branch_name': branch_name,
                    'year': year,
                    'role': random.choice(['Class Coordinator', 'Faculty Advisor', 'Subject Teacher']),
                    'subjects': random.sample(['Mathematics', 'Physics', 'Chemistry', 'Computer Science', 
                                              'Electronics', 'Mechanical Engineering', 'English', 'Data Structures'], 
                                             k=random.randint(1, 3))
                }
                
                teachers.append(teacher)
                teacher_id += 1
    
    # Save teachers data
    with open('data/teachers.json', 'w') as f:
        json.dump(teachers, f, indent=2)
    
    print(f"✅ Generated {len(teachers)} teachers")
    
    return teachers


def assign_students_to_teachers(teachers):
    """Assign students to teachers based on branch and year"""
    
    # Read student and analytics data
    students_df = pd.read_csv('data/dummy_data/01_students_master.csv')
    
    with open('student_analytics_results.json', 'r') as f:
        analytics = json.load(f)
    
    # Create analytics lookup
    analytics_dict = {a['student_id']: a for a in analytics}
    
    # Merge student basic info with analytics
    for idx, student in students_df.iterrows():
        student_id = student['student_id']
        if student_id in analytics_dict:
            analytics_dict[student_id].update({
                'roll_number': student['roll_number'],
                'full_name': student['full_name'],
                'email': student['email'],
                'branch': student['branch'],
                'year': student['year'],
                'semester': student['semester'],
                'gender': student['gender'],
                'location_type': student['location_type']
            })
    
    # Assign students to teachers
    student_teacher_mapping = []
    
    for teacher in teachers:
        # Get students matching this teacher's branch and year
        matching_students = students_df[
            (students_df['branch'] == teacher['branch']) & 
            (students_df['year'] == teacher['year'])
        ]
        
        # Randomly assign subset of students (teachers share students)
        sample_size = max(10, int(len(matching_students) * random.uniform(0.3, 0.6)))
        assigned = matching_students.sample(n=min(sample_size, len(matching_students)))
        
        for _, student in assigned.iterrows():
            student_teacher_mapping.append({
                'teacher_id': teacher['teacher_id'],
                'student_id': student['student_id']
            })
        
        print(f"Teacher {teacher['teacher_id']}: {len(assigned)} students assigned")
    
    # Save mapping
    with open('data/student_teacher_mapping.json', 'w') as f:
        json.dump(student_teacher_mapping, f, indent=2)
    
    # Save enriched analytics
    enriched_analytics = list(analytics_dict.values())
    with open('data/student_analytics_enriched.json', 'w') as f:
        json.dump(enriched_analytics, f, indent=2)
    
    print(f"\n✅ Created student-teacher mappings: {len(student_teacher_mapping)} assignments")
    print(f"✅ Saved enriched analytics: {len(enriched_analytics)} students")


if __name__ == "__main__":
    print("="*80)
    print("🎓 GENERATING TEACHER DATA & ASSIGNMENTS")
    print("="*80)
    
    # Generate teachers
    teachers = generate_teacher_data()
    
    # Assign students
    assign_students_to_teachers(teachers)
    
    print("\n" + "="*80)
    print("✅ TEACHER DATA GENERATION COMPLETE!")
    print("="*80)
    
    # Print sample credentials
    print("\n📋 SAMPLE TEACHER CREDENTIALS:")
    print("-" * 60)
    for teacher in teachers[:5]:
        print(f"Username: {teacher['username']}")
        print(f"Password: {teacher['password']}")
        print(f"Branch: {teacher['branch_name']} - Year {teacher['year']}")
        print(f"Email: {teacher['email']}")
        print("-" * 60)