"""
Student Dropout Prediction System - Flask API
Supports flexible student count with complete CRUD operations
"""
from flask import Flask, jsonify, request
from flask_cors import CORS
import sqlite3
import json
from functools import wraps
from datetime import date, datetime

app = Flask(__name__)
CORS(app)

# Database configuration
DATABASE = 'students.db'

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def query_db(query, args=(), one=False):
    """Execute query and return results"""
    conn = get_db()
    cur = conn.execute(query, args)
    rv = [dict(row) for row in cur.fetchall()]
    conn.close()
    return (rv[0] if rv else None) if one else rv

# ============================================================================
# AUTHENTICATION & AUTHORIZATION
# ============================================================================

@app.route('/api/auth/login', methods=['POST'])
def login():
    """User login endpoint"""
    data = request.json
    user_id = data.get('user_id')
    user_type = data.get('user_type')  # teacher, parent, student, admin
    password = data.get('password')
    
    # Simple authentication (enhance with real auth later)
    return jsonify({
        'success': True,
        'token': f'{user_type}_{user_id}',
        'user_type': user_type,
        'user_id': user_id
    })

# ============================================================================
# TEACHER ENDPOINTS
# ============================================================================

@app.route('/api/teachers/<int:teacher_id>/attendance/students', methods=['GET'])
def get_teacher_students_for_attendance(teacher_id):
    students = query_db("""
        SELECT 
            s.student_id,
            s.full_name,              -- keep if this column exists
            s.roll_number,
            s.branch,                 -- or s.branch_name if that's the column
            s.year
        FROM students s
        JOIN student_teacher_mapping stm ON s.student_id = stm.student_id
        WHERE stm.teacher_id = ?
        ORDER BY s.student_id
    """, (teacher_id,))
    return jsonify({'students': students})


@app.route('/api/teachers/<int:teacher_id>/attendance', methods=['POST'])
def submit_attendance(teacher_id):
    """
    Body: { date: '2025-12-05', records: [{student_id: 1, status: 'Present'}, ...] }
    """
    payload = request.get_json() or {}
    rec_date = payload.get('date') or str(date.today())
    records = payload.get('records', [])

    if not records:
        return jsonify({'error': 'No attendance records provided'}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        for r in records:
            sid = r.get('student_id')
            status = r.get('status')
            if not sid or status not in ('Present', 'Absent'):
                continue
            cur.execute("""
                INSERT INTO attendance (teacher_id, student_id, date, status)
                VALUES (?, ?, ?, ?)
            """, (teacher_id, sid, rec_date, status))
        conn.commit()
        return jsonify({'success': True, 'count': len(records), 'date': rec_date}), 200
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

@app.route('/api/teachers/<int:teacher_id>/resources', methods=['GET'])
def list_teacher_resources(teacher_id):
    rows = query_db("""
        SELECT * FROM resources
        WHERE teacher_id = ?
        ORDER BY datetime(created_at) DESC
    """, (teacher_id,))
    return jsonify({'resources': rows})


@app.route('/api/teachers/<int:teacher_id>/resources', methods=['POST'])
def create_teacher_resource(teacher_id):
    data = request.get_json() or {}
    title = data.get('title')
    rtype = data.get('type')
    url = data.get('url')
    desc = data.get('description')

    if not title or not rtype:
        return jsonify({'error': 'title and type are required'}), 400

    conn = get_db()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO resources (teacher_id, title, description, type, url, file_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            teacher_id,
            title,
            desc,
            rtype,
            url,
            None,
            datetime.utcnow().isoformat()
        ))
        conn.commit()
        return jsonify({'success': True, 'id': cur.lastrowid}), 201
    except Exception as e:
        conn.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()
@app.route('/api/teachers/<int:teacher_id>/dashboard', methods=['GET'])
def teacher_dashboard(teacher_id):
    """Get complete dashboard for teacher"""
    try:
        conn = get_db()
        cursor = conn.cursor()
        
        # Get teacher info
        cursor.execute('SELECT * FROM teachers WHERE teacher_id = ?', (teacher_id,))
        teacher_row = cursor.fetchone()
        
        if not teacher_row:
            conn.close()
            return jsonify({'error': 'Teacher not found'}), 404
        
        teacher = dict(teacher_row)
        
        # Get all students mapped to this teacher
        cursor.execute('''
            SELECT s.* 
            FROM students s
            JOIN student_teacher_mapping stm ON s.student_id = stm.student_id
            WHERE stm.teacher_id = ?
            ORDER BY s.student_id
        ''', (teacher_id,))
        
        student_rows = cursor.fetchall()
        students = [dict(row) for row in student_rows]
        
        if not students:
            conn.close()
            return jsonify({
                'teacher': teacher,
                'statistics': {
                    'total_students': 0,
                    'high_risk': 0,
                    'medium_risk': 0,
                    'low_risk': 0,
                    'average_gpa': 0,
                    'average_attendance': 0
                },
                'students': []
            })
        
        # Get predictions for these students
        student_ids = [s['student_id'] for s in students]
        placeholders = ','.join('?' * len(student_ids))
        
        cursor.execute(f'''
            SELECT * FROM predictions 
            WHERE student_id IN ({placeholders})
        ''', student_ids)
        
        prediction_rows = cursor.fetchall()
        predictions_dict = {dict(row)['student_id']: dict(row) for row in prediction_rows}
        
        # Merge predictions with students
        for student in students:
            student_id = student['student_id']
            if student_id in predictions_dict:
                pred = predictions_dict[student_id]
                student['dropout_risk'] = pred.get('dropout_risk', 'Unknown')
                student['dropout_risk_score'] = pred.get('dropout_risk_score', 0)
                student['recommendations'] = pred.get('recommendations', '')
            else:
                student['dropout_risk'] = 'Unknown'
                student['dropout_risk_score'] = 0
                student['recommendations'] = ''
        
        conn.close()
        
        # Calculate statistics
        total = len(students)
        high_risk = sum(1 for s in students if s.get('dropout_risk') == 'High Risk')
        medium_risk = sum(1 for s in students if s.get('dropout_risk') == 'Medium Risk')
        low_risk = sum(1 for s in students if s.get('dropout_risk') == 'Low Risk')
        
        # Calculate averages (handle None values)
        gpas = [float(s.get('current_semester_gpa') or 0) for s in students]
        attendances = [float(s.get('attendance_percentage') or 0) for s in students]
        
        avg_gpa = sum(gpas) / len(gpas) if gpas else 0
        avg_attendance = sum(attendances) / len(attendances) if attendances else 0
        
        return jsonify({
            'teacher': teacher,
            'statistics': {
                'total_students': total,
                'high_risk': high_risk,
                'medium_risk': medium_risk,
                'low_risk': low_risk,
                'average_gpa': round(avg_gpa, 2),
                'average_attendance': round(avg_attendance, 1)
            },
            'students': students
        })
        
    except Exception as e:
        print(f"❌ Error in teacher_dashboard: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/teachers/<int:teacher_id>/students', methods=['GET'])
def teacher_students(teacher_id):
    """Get paginated list of students"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    risk_filter = request.args.get('risk_filter', 'all')
    
    offset = (page - 1) * per_page
    
    # Build query with optional risk filter
    base_query = '''
        SELECT s.*, p.dropout_risk, p.dropout_risk_score
        FROM students s
        LEFT JOIN predictions p ON s.student_id = p.student_id
        JOIN student_teacher_mapping stm ON s.student_id = stm.student_id
        WHERE stm.teacher_id = ?
    '''
    
    if risk_filter != 'all':
        base_query += f" AND p.dropout_risk = '{risk_filter}'"
    
    base_query += " ORDER BY s.student_id LIMIT ? OFFSET ?"
    
    students = query_db(base_query, (teacher_id, per_page, offset))
    
    # Get total count
    count_query = '''
        SELECT COUNT(*) as count FROM student_teacher_mapping
        WHERE teacher_id = ?
    '''
    total = query_db(count_query, (teacher_id,), one=True)['count']
    
    return jsonify({
        'students': students,
        'pagination': {
            'page': page,
            'per_page': per_page,
            'total': total,
            'pages': (total + per_page - 1) // per_page
        }
    })

@app.route('/api/teachers/<int:teacher_id>/student/<int:student_id>', methods=['GET'])
def teacher_student_detail(teacher_id, student_id):
    """Get detailed view of specific student"""
    try:
        # Verify teacher-student relationship
        mapping = query_db('''
            SELECT * FROM student_teacher_mapping
            WHERE teacher_id = ? AND student_id = ?
        ''', (teacher_id, student_id), one=True)
        
        if not mapping:
            return jsonify({'error': 'Student not assigned to this teacher'}), 403
        
        # Get student data
        student = query_db('SELECT * FROM students WHERE student_id = ?', 
                          (student_id,), one=True)
        predictions = query_db('SELECT * FROM predictions WHERE student_id = ?', 
                              (student_id,), one=True)
        
        return jsonify({
            'student': student,
            'predictions': predictions
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# PARENT ENDPOINTS
# ============================================================================

@app.route('/api/parents/<int:parent_id>/children', methods=['GET'])
def parent_children(parent_id):
    """Get list of parent's children"""
    # In real system, link parent_id to students via parent table
    # For now, using student_id as proxy
    students = query_db('''
        SELECT s.*, p.dropout_risk, p.dropout_risk_score
        FROM students s
        LEFT JOIN predictions p ON s.student_id = p.student_id
        WHERE s.student_id = ?
    ''', (parent_id,))
    
    return jsonify({'children': students})

@app.route('/api/parents/<int:parent_id>/child/<int:student_id>', methods=['GET'])
def get_child_profile(parent_id, student_id):
    """Get detailed profile of child"""
    student = query_db('SELECT * FROM students WHERE student_id = ?', 
                      (student_id,), one=True)
    predictions = query_db('SELECT * FROM predictions WHERE student_id = ?', 
                          (student_id,), one=True)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Parse recommendations if stored as JSON string
    if predictions and predictions.get('recommendations'):
        try:
            if isinstance(predictions['recommendations'], str):
                predictions['recommendations'] = json.loads(predictions['recommendations'])
        except:
            pass
    
    return jsonify({
        'student': student,
        'predictions': predictions
    })

# ============================================================================
# STUDENT ENDPOINTS
# ============================================================================



@app.route('/api/students/<int:student_id>/dashboard', methods=['GET'])
def student_dashboard(student_id):
    """Get student's personal dashboard"""
    student = query_db('SELECT * FROM students WHERE student_id = ?', 
                      (student_id,), one=True)
    predictions = query_db('SELECT * FROM predictions WHERE student_id = ?', 
                          (student_id,), one=True)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Parse recommendations
    if predictions and predictions.get('recommendations'):
        try:
            if isinstance(predictions['recommendations'], str):
                predictions['recommendations'] = json.loads(predictions['recommendations'])
        except:
            pass
    
    return jsonify({
        'student': student,
        'predictions': predictions
    })

@app.route('/api/students/<int:student_id>/performance', methods=['GET'])
def student_performance(student_id):
    """Get detailed performance metrics"""
    student = query_db('SELECT * FROM students WHERE student_id = ?', 
                      (student_id,), one=True)
    
    if not student:
        return jsonify({'error': 'Student not found'}), 404
    
    # Extract performance metrics
    performance = {
        'academic': {
            'current_gpa': student.get('current_semester_gpa'),
            'previous_gpa': student.get('previous_semester_gpa'),
            'cumulative_gpa': student.get('cumulative_gpa'),
            'gpa_trend': student.get('gpa_trend')
        },
        'attendance': {
            'percentage': student.get('attendance_percentage'),
            'first_half': student.get('attendance_first_half'),
            'second_half': student.get('attendance_second_half'),
            'trend': student.get('attendance_trend')
        },
        'subjects': {
            'chemistry': student.get('marks_subject_chemistry'),
            'computer_science': student.get('marks_subject_computer_science'),
            'electronics': student.get('marks_subject_electronics'),
            'mathematics': student.get('marks_subject_mathematics'),
            'physics': student.get('marks_subject_physics')
        }
    }
    
    return jsonify(performance)
@app.route('/api/students/<int:student_id>/resources', methods=['GET'])
def student_resources(student_id):
    print("🔎 /api/students/%d/resources called" % student_id)
    teachers = query_db("""
        SELECT teacher_id
        FROM student_teacher_mapping
        WHERE student_id = ?
    """, (student_id,))
    teacher_ids = [t['teacher_id'] for t in teachers]

    if not teacher_ids:
        return jsonify({'resources': []})

    placeholders = ','.join('?' * len(teacher_ids))
    rows = query_db(f"""
        SELECT r.*, t.name as teacher_name
        FROM resources r
        JOIN teachers t ON r.teacher_id = t.teacher_id
        WHERE r.teacher_id IN ({placeholders})
        ORDER BY datetime(r.created_at) DESC
    """, tuple(teacher_ids))

    return jsonify({'resources': rows})


# ============================================================================
# ADMIN ENDPOINTS
# ============================================================================

@app.route('/api/admin/dashboard', methods=['GET'])
def admin_dashboard():
    """Get system-wide admin dashboard"""
    try:
        # Get counts
        total_students = query_db('SELECT COUNT(*) as count FROM students', one=True)['count']
        total_teachers = query_db('SELECT COUNT(*) as count FROM teachers', one=True)['count']
        
        # Risk distribution
        risk_stats = query_db('''
            SELECT dropout_risk, COUNT(*) as count
            FROM predictions
            GROUP BY dropout_risk
        ''')
        
        risk_dist = {item['dropout_risk']: item['count'] for item in risk_stats}
        
        # Branch-wise stats
        branch_stats = query_db('''
            SELECT s.branch, COUNT(*) as total,
                   SUM(CASE WHEN p.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) as high_risk
            FROM students s
            LEFT JOIN predictions p ON s.student_id = p.student_id
            GROUP BY s.branch
        ''')
        
        # Year-wise stats
        year_stats = query_db('''
            SELECT s.year, COUNT(*) as total,
                   SUM(CASE WHEN p.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) as high_risk
            FROM students s
            LEFT JOIN predictions p ON s.student_id = p.student_id
            GROUP BY s.year
        ''')
        
        return jsonify({
            'overview': {
                'total_students': total_students,
                'total_teachers': total_teachers,
                'total_mappings': query_db('SELECT COUNT(*) as count FROM student_teacher_mapping', one=True)['count']
            },
            'risk_distribution': risk_dist,
            'branch_statistics': branch_stats,
            'year_statistics': year_stats
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students', methods=['GET'])
def admin_students():
    """Get all students with filters"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 50, type=int)
    branch = request.args.get('branch')
    year = request.args.get('year', type=int)
    risk = request.args.get('risk')
    
    offset = (page - 1) * per_page
    
    # Build dynamic query
    query = '''
        SELECT s.*, p.dropout_risk, p.dropout_risk_score
        FROM students s
        LEFT JOIN predictions p ON s.student_id = p.student_id
        WHERE 1=1
    '''
    params = []
    
    if branch:
        query += ' AND s.branch = ?'
        params.append(branch)
    if year:
        query += ' AND s.year = ?'
        params.append(year)
    if risk:
        query += ' AND p.dropout_risk = ?'
        params.append(risk)
    
    query += ' ORDER BY s.student_id LIMIT ? OFFSET ?'
    params.extend([per_page, offset])
    
    students = query_db(query, tuple(params))
    
    return jsonify({'students': students, 'page': page})

@app.route('/api/admin/reports/risk-summary', methods=['GET'])
def risk_summary_report():
    """Generate risk summary report"""
    summary = query_db('''
        SELECT 
            s.branch,
            s.year,
            COUNT(*) as total_students,
            SUM(CASE WHEN p.dropout_risk = 'High Risk' THEN 1 ELSE 0 END) as high_risk,
            SUM(CASE WHEN p.dropout_risk = 'Medium Risk' THEN 1 ELSE 0 END) as medium_risk,
            SUM(CASE WHEN p.dropout_risk = 'Low Risk' THEN 1 ELSE 0 END) as low_risk,
            AVG(s.current_semester_gpa) as avg_gpa,
            AVG(s.attendance_percentage) as avg_attendance
        FROM students s
        LEFT JOIN predictions p ON s.student_id = p.student_id
        GROUP BY s.branch, s.year
        ORDER BY s.branch, s.year
    ''')
    
    return jsonify({'report': summary})

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        conn = get_db()
        conn.execute('SELECT 1')
        conn.close()
        return jsonify({'status': 'healthy', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/api/stats', methods=['GET'])
def system_stats():
    """Get system statistics"""
    try:
        stats = {
            'students': query_db('SELECT COUNT(*) as count FROM students', one=True)['count'],
            'teachers': query_db('SELECT COUNT(*) as count FROM teachers', one=True)['count'],
            'mappings': query_db('SELECT COUNT(*) as count FROM student_teacher_mapping', one=True)['count'],
            'predictions': query_db('SELECT COUNT(*) as count FROM predictions', one=True)['count']
        }
        return jsonify({'statistics': stats, 'status': 'operational'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found', 'status': 404}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error', 'status': 500}), 500

# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("=" * 70)
    print("🚀 STUDENT DROPOUT PREDICTION SYSTEM - API SERVER")
    print("=" * 70)
    print(f"\n📍 Server running at: http://localhost:5000")
    print(f"📊 Check stats at: http://localhost:5000/api/stats")
    print(f"💚 Health check at: http://localhost:5000/api/health")
    print("\nPress CTRL+C to stop the server\n")
    print("=" * 70)
    
    app.run(debug=True, port=5000, host='0.0.0.0')