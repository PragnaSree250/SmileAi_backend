import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'smile_ai',
    'port': 3307
}

def migrate():
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        print("Updating 'cases' table...")
        
        # 1. Rename clinical_condition to condition
        # First check if condition already exists to avoid errors
        cursor.execute("DESCRIBE cases")
        cols = [col[0] for col in cursor.fetchall()]
        
        if 'clinical_condition' in cols and 'condition' not in cols:
            print("Renaming 'clinical_condition' to 'condition'...")
            cursor.execute("ALTER TABLE cases CHANGE clinical_condition `condition` VARCHAR(255)")
        
        # 2. Add missing columns
        missing_columns = {
            'patient_phone': 'VARCHAR(20) AFTER patient_gender',
            'medical_history': 'TEXT AFTER patient_phone',
            'intercanine_width': 'VARCHAR(50) AFTER shade',
            'incisor_length': 'VARCHAR(50) AFTER intercanine_width',
            'abutment_health': 'VARCHAR(100) AFTER incisor_length',
            'gingival_architecture': 'VARCHAR(100) AFTER abutment_health'
        }
        
        for col_name, col_def in missing_columns.items():
            if col_name not in cols:
                print(f"Adding column '{col_name}'...")
                cursor.execute(f"ALTER TABLE cases ADD COLUMN {col_name} {col_def}")

        # 3. Create missing tables
        tables = {
            'medications': """
                CREATE TABLE IF NOT EXISTS medications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    case_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    dosage VARCHAR(100),
                    frequency VARCHAR(100),
                    duration VARCHAR(100),
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                )
            """,
            'reports': """
                CREATE TABLE IF NOT EXISTS reports (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    case_id INT NOT NULL,
                    deficiency_addressed TEXT,
                    ai_reasoning TEXT,
                    risk_analysis TEXT,
                    aesthetic_prognosis TEXT,
                    placement_strategy TEXT,
                    final_recommendation TEXT,
                    hyperdontia_status VARCHAR(50),
                    aesthetic_symmetry VARCHAR(50),
                    golden_ratio VARCHAR(50),
                    missing_teeth_status VARCHAR(50),
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                )
            """,
            'care_tips': """
                CREATE TABLE IF NOT EXISTS care_tips (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    case_id INT NOT NULL,
                    tip_text TEXT NOT NULL,
                    is_positive BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                )
            """,
            'notifications': """
                CREATE TABLE IF NOT EXISTS notifications (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    title VARCHAR(255) NOT NULL,
                    message TEXT NOT NULL,
                    is_read BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES register(id) ON DELETE CASCADE
                )
            """,
            'case_timeline': """
                CREATE TABLE IF NOT EXISTS case_timeline (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    case_id INT NOT NULL,
                    event_title VARCHAR(255) NOT NULL,
                    event_description TEXT,
                    event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
                )
            """
        }

        for table_name, create_sql in tables.items():
            print(f"Creating table '{table_name}' if not exists...")
            cursor.execute(create_sql)

        conn.commit()
        print("Migration completed successfully!")
        
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Error during migration: {e}")

if __name__ == "__main__":
    migrate()
