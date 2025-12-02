"""
Student Dropout Prediction System - Data Loader (FIXED)
Automatically loads ALL 5 data files with ANY number of students
Handles complex data types (lists, dicts) by converting to JSON
"""
import sqlite3
import pandas as pd
import json
import os
from pathlib import Path

class DataLoader:
    def __init__(self, data_dir='data', db_name='students.db'):
        self.data_dir = Path(data_dir)
        self.db_name = db_name
        self.conn = None
        
    def load_all_data(self):
        """Load all 5 data files into SQLite database"""
        print("=" * 60)
        print("📦 STUDENT DROPOUT PREDICTION SYSTEM - DATA LOADER")
        print("=" * 60)
        
        # Check if data directory exists
        if not self.data_dir.exists():
            print(f"❌ Error: Data directory '{self.data_dir}' not found!")
            return False
        
        try:
            # Connect to database
            self.conn = sqlite3.connect(self.db_name)
            print(f"\n✅ Connected to database: {self.db_name}")
            
            # Load each file
            success = (
                self._load_students() and
                self._load_predictions() and
                self._load_analytics() and
                self._load_teachers() and
                self._load_mappings()
            )
            
            if success:
                self._print_summary()
                print("\n" + "=" * 60)
                print("✅ ALL DATA LOADED SUCCESSFULLY!")
                print("=" * 60)
                return True
            else:
                print("\n❌ Data loading failed!")
                return False
                
        except Exception as e:
            print(f"\n❌ Fatal error: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            if self.conn:
                self.conn.close()
    
    def _convert_complex_columns(self, df):
        """Convert dict and list columns to JSON strings"""
        for col in df.columns:
            # Check if column contains complex types
            if len(df) > 0:
                first_val = df[col].iloc[0]
                if isinstance(first_val, (dict, list)):
                    print(f"      Converting column '{col}' to JSON")
                    df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (dict, list)) else x)
        return df
    
    def _load_students(self):
        """Load processed_data.csv - Student base data"""
        print("\n📂 Loading student data...")
        try:
            file_path = 'processed_data.csv'
            df = pd.read_csv(file_path)
            
            # Convert complex columns to JSON
            df = self._convert_complex_columns(df)
            
            df.to_sql('students', self.conn, if_exists='replace', index=False)
            print(f"   ✅ Loaded {len(df)} students from processed_data.csv")
            return True
        except FileNotFoundError:
            print(f"   ❌ Error: File not found at {file_path}")
            return False
        except Exception as e:
            print(f"   ❌ Error loading students: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_predictions(self):
        """Load student_predictions.csv - ML predictions"""
        print("\n🔮 Loading predictions...")
        try:
            file_path ='student_predictions.csv'
            df = pd.read_csv(file_path)
            
            # Convert recommendations column if it exists
            if 'recommendations' in df.columns:
                print("      Converting 'recommendations' column to JSON")
                df['recommendations'] = df['recommendations'].apply(
                    lambda x: json.dumps(x) if isinstance(x, (dict, list)) else str(x)
                )
            
            # Convert any other complex columns
            df = self._convert_complex_columns(df)
            
            df.to_sql('predictions', self.conn, if_exists='replace', index=False)
            print(f"   ✅ Loaded {len(df)} predictions from student_predictions.csv")
            return True
        except FileNotFoundError:
            print(f"   ❌ Error: File not found at {file_path}")
            return False
        except Exception as e:
            print(f"   ❌ Error loading predictions: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_analytics(self):
        """Load student_analytics_results.json - Detailed analytics"""
        print("\n📊 Loading analytics...")
        try:
            file_path ='student_analytics_results.json'
            
            if not file_path.exists():
                print(f"   ⚠️  Analytics file not found, skipping")
                return True
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                # If it's a single dict, wrap in list
                if 'student_id' in data or len(data) > 0:
                    df = pd.DataFrame([data])
                else:
                    # If it's nested dicts with student_ids as keys
                    df = pd.DataFrame.from_dict(data, orient='index')
                    df.reset_index(inplace=True)
                    df.rename(columns={'index': 'student_id'}, inplace=True)
            else:
                df = pd.DataFrame()
            
            if not df.empty:
                # Convert complex columns to JSON
                df = self._convert_complex_columns(df)
                
                df.to_sql('analytics', self.conn, if_exists='replace', index=False)
                print(f"   ✅ Loaded {len(df)} analytics records from student_analytics_results.json")
            else:
                print(f"   ⚠️  Analytics file is empty or invalid format")
            return True
            
        except FileNotFoundError:
            print(f"   ⚠️  Analytics file not found, skipping")
            return True
        except Exception as e:
            print(f"   ⚠️  Warning: Could not load analytics: {e}")
            # Analytics is optional, so return True
            return True
    
    def _load_teachers(self):
        """Load teachers.json - Faculty information"""
        print("\n👨‍🏫 Loading teachers...")
        try:
            file_path = self.data_dir / 'teachers.json'
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("Invalid teachers.json format")
            
            # Convert complex columns to JSON (e.g., subjects taught as list)
            df = self._convert_complex_columns(df)
            
            df.to_sql('teachers', self.conn, if_exists='replace', index=False)
            print(f"   ✅ Loaded {len(df)} teachers from teachers.json")
            return True
            
        except FileNotFoundError:
            print(f"   ❌ Error: File not found at {file_path}")
            return False
        except Exception as e:
            print(f"   ❌ Error loading teachers: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _load_mappings(self):
        """Load student_teacher_mapping.json - Student-Teacher relationships"""
        print("\n🔗 Loading student-teacher mappings...")
        try:
            file_path = self.data_dir / 'student_teacher_mapping.json'
            
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Convert to DataFrame
            if isinstance(data, list):
                df = pd.DataFrame(data)
            elif isinstance(data, dict):
                df = pd.DataFrame([data])
            else:
                raise ValueError("Invalid student_teacher_mapping.json format")
            
            # Convert complex columns to JSON
            df = self._convert_complex_columns(df)
            
            df.to_sql('student_teacher_mapping', self.conn, if_exists='replace', index=False)
            print(f"   ✅ Loaded {len(df)} mappings from student_teacher_mapping.json")
            return True
            
        except FileNotFoundError:
            print(f"   ❌ Error: File not found at {file_path}")
            return False
        except Exception as e:
            print(f"   ❌ Error loading mappings: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def _print_summary(self):
        """Print data summary"""
        cursor = self.conn.cursor()
        
        print("\n" + "=" * 60)
        print("📊 DATA SUMMARY")
        print("=" * 60)
        
        # Count records in each table
        tables = ['students', 'predictions', 'teachers', 'student_teacher_mapping', 'analytics']
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"   {table.replace('_', ' ').title():<30} {count:>6} records")
            except sqlite3.OperationalError:
                print(f"   {table.replace('_', ' ').title():<30}      0 records (table not created)")
        
        # Risk distribution
        try:
            cursor.execute("""
                SELECT dropout_risk, COUNT(*) as count 
                FROM predictions 
                GROUP BY dropout_risk
            """)
            print(f"\n   Risk Distribution:")
            for risk, count in cursor.fetchall():
                print(f"      {risk:<20} {count:>6} students")
        except sqlite3.OperationalError:
            pass

# ============================================
# Command-line execution
# ============================================

if __name__ == '__main__':
    import sys
    
    # Check if custom data directory provided
    data_dir = sys.argv[1] if len(sys.argv) > 1 else 'data'
    
    # Check if data directory exists
    if not os.path.exists(data_dir):
        print(f"❌ Error: Data directory '{data_dir}' not found!")
        print(f"\n💡 Usage: python data_loader.py [data_directory]")
        print(f"   Example: python data_loader.py data")
        sys.exit(1)
    
    # Create loader and load data
    loader = DataLoader(data_dir=data_dir)
    success = loader.load_all_data()
    
    if success:
        print("\n✅ Ready to start the Flask server!")
        print("   Run: python app.py")
    else:
        print("\n❌ Data loading failed. Please check your data files.")
        print("\n📋 Expected files in 'data/' directory:")
        print("   1. processed_data.csv")
        print("   2. student_predictions.csv")
        print("   3. student_analytics_results.json (optional)")
        print("   4. teachers.json")
        print("   5. student_teacher_mapping.json")
    
    sys.exit(0 if success else 1)