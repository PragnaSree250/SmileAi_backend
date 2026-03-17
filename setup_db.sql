-- SmileAI Optimized Database Schema
-- Database: smile_ai

-- 1. Register Table (Authentication & User Details)
-- Minimal and essential for login/signup
CREATE TABLE IF NOT EXISTS register (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) DEFAULT 'dentist',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Cases Table (Core Patient Case Data)
-- Removed: patient_dob, patient_gender, scan_id, status (simplified)
CREATE TABLE IF NOT EXISTS cases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    dentist_id INT NOT NULL,
    patient_first_name VARCHAR(100) NOT NULL,
    patient_last_name VARCHAR(100) NOT NULL,
    
    -- Clinical Details from UI
    restoration_type VARCHAR(50),
    material VARCHAR(50),
    shade VARCHAR(10),
    
    -- AI Analysis Results
    ai_deficiency VARCHAR(100),
    ai_report TEXT,
    ai_score INT,
    ai_grade VARCHAR(2),
    ai_recommendation TEXT,
    
    -- Visual Assets
    face_photo_path VARCHAR(255),
    intra_photo_path VARCHAR(255),
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (dentist_id) REFERENCES register(id) ON DELETE CASCADE
);

-- 3. Case Files Table (Metadata for every uploaded file)
CREATE TABLE IF NOT EXISTS case_files (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    file_path VARCHAR(255) NOT NULL,
    file_type ENUM('IMAGE','STL','JSON','PDF') NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
);

-- 4. Reports Table (Simplified for finalized summaries)
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    case_id INT NOT NULL,
    deficiency_addressed TEXT,
    ai_reasoning TEXT,
    final_recommendation TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (case_id) REFERENCES cases(id) ON DELETE CASCADE
);

-- 5. Healing Logs (User tracking)
CREATE TABLE IF NOT EXISTS healing_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    image_url TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES register(id) ON DELETE CASCADE
);