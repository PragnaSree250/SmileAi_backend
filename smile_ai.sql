-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1:3307
-- Generation Time: Mar 25, 2026 at 11:07 AM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `smile_ai`
--

-- --------------------------------------------------------

--
-- Table structure for table `appointments`
--

CREATE TABLE `appointments` (
  `id` int(11) NOT NULL,
  `case_id` int(11) NOT NULL,
  `patient_id` varchar(50) NOT NULL,
  `dentist_id` int(11) NOT NULL,
  `appointment_date` date NOT NULL,
  `appointment_day` varchar(20) NOT NULL,
  `status` varchar(20) DEFAULT 'Scheduled',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `care_tips`
--

CREATE TABLE `care_tips` (
  `id` int(11) NOT NULL,
  `case_id` int(11) NOT NULL,
  `tip_text` text NOT NULL,
  `is_positive` tinyint(1) DEFAULT 1,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `cases`
--

CREATE TABLE `cases` (
  `id` int(11) NOT NULL,
  `dentist_id` int(11) NOT NULL,
  `patient_id` varchar(50) DEFAULT NULL,
  `patient_first_name` varchar(100) NOT NULL,
  `patient_last_name` varchar(100) NOT NULL,
  `patient_dob` varchar(20) DEFAULT NULL,
  `patient_gender` varchar(20) DEFAULT NULL,
  `patient_phone` varchar(20) DEFAULT NULL,
  `medical_history` text DEFAULT NULL,
  `tooth_numbers` varchar(100) DEFAULT NULL,
  `condition` varchar(255) DEFAULT NULL,
  `scan_id` varchar(100) DEFAULT NULL,
  `restoration_type` varchar(50) DEFAULT NULL,
  `material` varchar(50) DEFAULT NULL,
  `shade` varchar(10) DEFAULT NULL,
  `intercanine_width` varchar(50) DEFAULT NULL,
  `incisor_length` varchar(50) DEFAULT NULL,
  `abutment_health` varchar(100) DEFAULT NULL,
  `gingival_architecture` varchar(100) DEFAULT NULL,
  `ai_deficiency` varchar(100) DEFAULT NULL,
  `ai_report` text DEFAULT NULL,
  `ai_score` int(11) DEFAULT NULL,
  `ai_grade` varchar(2) DEFAULT NULL,
  `ai_recommendation` text DEFAULT NULL,
  `caries_status` varchar(255) DEFAULT NULL,
  `hypodontia_status` varchar(255) DEFAULT NULL,
  `discoloration_status` varchar(255) DEFAULT NULL,
  `gum_inflammation_status` varchar(255) DEFAULT NULL,
  `calculus_status` varchar(255) DEFAULT NULL,
  `redness_analysis` varchar(255) DEFAULT NULL,
  `aesthetic_symmetry` varchar(255) DEFAULT NULL,
  `face_photo_path` varchar(255) DEFAULT NULL,
  `intra_photo_path` varchar(255) DEFAULT NULL,
  `status` varchar(20) DEFAULT 'Active',
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `suggested_restoration` varchar(255) DEFAULT NULL,
  `suggested_material` varchar(255) DEFAULT NULL,
  `hyperdontia_status` varchar(255) DEFAULT NULL,
  `risk_analysis` text DEFAULT NULL,
  `aesthetic_prognosis` text DEFAULT NULL,
  `placement_strategy` text DEFAULT NULL,
  `golden_ratio` varchar(50) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `cases`
--

INSERT INTO `cases` (`id`, `dentist_id`, `patient_id`, `patient_first_name`, `patient_last_name`, `patient_dob`, `patient_gender`, `patient_phone`, `medical_history`, `tooth_numbers`, `condition`, `scan_id`, `restoration_type`, `material`, `shade`, `intercanine_width`, `incisor_length`, `abutment_health`, `gingival_architecture`, `ai_deficiency`, `ai_report`, `ai_score`, `ai_grade`, `ai_recommendation`, `caries_status`, `hypodontia_status`, `discoloration_status`, `gum_inflammation_status`, `calculus_status`, `redness_analysis`, `aesthetic_symmetry`, `face_photo_path`, `intra_photo_path`, `status`, `created_at`, `suggested_restoration`, `suggested_material`, `hyperdontia_status`, `risk_analysis`, `aesthetic_prognosis`, `placement_strategy`, `golden_ratio`) VALUES
(62, 20, 'P0015', 'keerthana', 'Doe', '2011-01-12', 'Female', NULL, NULL, '12', 'Caries', '-', 'Crown', 'PFM', 'A3', NULL, NULL, NULL, NULL, 'Healthy', 'Clinical analysis indicates healthy dental structure with 80.2% confidence.', 90, 'A', 'Standard preventative care.', 'No major carious lesions detected.', 'Normal', 'Minimal staining.', 'Healthy', 'Low', 'Normal', 'Awaiting Measurement', 'uploads/case_62_7e94_face_photo_upload.jpg', 'uploads/case_62_394e_intra_photo_upload.jpg', 'Completed', '2026-03-25 07:18:37', 'N/A', 'N/A', NULL, 'Minimal clinical risk; maintain routine hygiene.', 'Excellent. Stable with standard care.', 'Preventative maintenance and regular checkups.', 'Variable Match');

-- --------------------------------------------------------

--
-- Table structure for table `case_files`
--

CREATE TABLE `case_files` (
  `id` int(11) NOT NULL,
  `case_id` int(11) NOT NULL,
  `file_path` varchar(255) NOT NULL,
  `file_type` varchar(20) NOT NULL,
  `uploaded_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `case_files`
--

INSERT INTO `case_files` (`id`, `case_id`, `file_path`, `file_type`, `uploaded_at`) VALUES
(123, 62, 'uploads/case_62_7e94_face_photo_upload.jpg', 'IMAGE', '2026-03-25 07:18:37'),
(124, 62, 'uploads/case_62_394e_intra_photo_upload.jpg', 'IMAGE', '2026-03-25 07:18:39');

-- --------------------------------------------------------

--
-- Table structure for table `case_timeline`
--

CREATE TABLE `case_timeline` (
  `id` int(11) NOT NULL,
  `case_id` int(11) NOT NULL,
  `event_title` varchar(255) NOT NULL,
  `event_description` text DEFAULT NULL,
  `event_time` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `dentist_profiles`
--

CREATE TABLE `dentist_profiles` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `dentist_id` varchar(50) DEFAULT NULL,
  `specialization` varchar(100) DEFAULT NULL,
  `clinic_address` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `dentist_profiles`
--

INSERT INTO `dentist_profiles` (`id`, `user_id`, `dentist_id`, `specialization`, `clinic_address`, `created_at`) VALUES
(1, 7, 'D5623', 'orthodontics', 'Chennai', '2026-03-13 04:51:52'),
(4, 9, 'D3192', '', 'hyderabad', '2026-03-13 04:57:15'),
(6, 20, 'D3311', NULL, NULL, '2026-03-24 08:42:28');

-- --------------------------------------------------------

--
-- Table structure for table `healing_logs`
--

CREATE TABLE `healing_logs` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `image_url` text DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `medications`
--

CREATE TABLE `medications` (
  `id` int(11) NOT NULL,
  `case_id` int(11) NOT NULL,
  `name` varchar(255) NOT NULL,
  `dosage` varchar(100) DEFAULT NULL,
  `frequency` varchar(100) DEFAULT NULL,
  `duration` varchar(100) DEFAULT NULL,
  `notes` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

-- --------------------------------------------------------

--
-- Table structure for table `notifications`
--

CREATE TABLE `notifications` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `title` varchar(255) NOT NULL,
  `message` text NOT NULL,
  `is_read` tinyint(1) DEFAULT 0,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `notifications`
--

INSERT INTO `notifications` (`id`, `user_id`, `title`, `message`, `is_read`, `created_at`) VALUES
(1, 15, 'New Appointment Scheduled', 'Your appointment for Case #21 has been fixed for 2026-3-15 (Sunday).', 0, '2026-03-16 16:21:46'),
(2, 15, 'New Appointment Scheduled', 'Your appointment for Case #21 has been fixed for 2026-3-17 (Tuesday).', 0, '2026-03-16 16:21:52');

-- --------------------------------------------------------

--
-- Table structure for table `register`
--

CREATE TABLE `register` (
  `id` int(11) NOT NULL,
  `full_name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `password` varchar(255) NOT NULL,
  `role` varchar(50) NOT NULL,
  `dentist_id` varchar(50) DEFAULT NULL,
  `patient_id` varchar(50) DEFAULT NULL,
  `phone` varchar(20) DEFAULT NULL,
  `specialization` varchar(100) DEFAULT NULL,
  `clinic_address` text DEFAULT NULL,
  `plan_type` varchar(20) DEFAULT 'Free',
  `profile_photo` varchar(255) DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `reset_token` varchar(10) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `register`
--

INSERT INTO `register` (`id`, `full_name`, `email`, `password`, `role`, `dentist_id`, `patient_id`, `phone`, `specialization`, `clinic_address`, `plan_type`, `profile_photo`, `created_at`, `reset_token`) VALUES
(7, 'Pragna sree Balijapelly', 'pragna050227@gmail.com', 'scrypt:32768:8:1$2EBjX124dmdqq6dN$b207d408d72cf43ef72c796e75217163668a69df1fb50e0d44a907efdfe0dc69d2224e7e54425843021a3fd66e22d924a5c34c10f57598aa8827bb8cd610778a', 'dentist', 'D5623', NULL, NULL, 'orthodontics', 'Chennai', 'Free', NULL, '2026-03-13 04:13:21', NULL),
(9, 'pragna balijapelly', 'pragnasreebalijapelly@gmail.com', 'scrypt:32768:8:1$mg7xlTvI10NzVMwn$f8a726888d46f2d5985e98a532cf86872553d1595dbbd0ce65aa56dffc80cc796d2f2d24d310213930f192a2ffbc8982802ee398798c6da428cc3cbc80e3192b', 'dentist', 'D3192', NULL, '8688002901', NULL, NULL, 'Free', NULL, '2026-03-13 04:57:15', NULL),
(15, 'keerthana pendem', 'pendemkeerthanamar@gmail.com', 'scrypt:32768:8:1$oa5qRqNyc5Jyla28$51671880f6c1ecaf11dd2beec2219f63d12aa2419d1810fdbaf726275787cf53fd408cd4f1c4bc4ce06c3d63b5518c9d72dc7d2acc082812a4d36b8274071ef5', 'patient', NULL, 'P0015', '9876543210', NULL, NULL, 'Free', NULL, '2026-03-16 12:50:32', NULL),
(18, 'himaja pendem', 'himajakotipalli@gmail.com', 'scrypt:32768:8:1$mWrFcgRDxhV4Yt8Z$88589c75bda55c5b177ae7d97055d4d338b203323ce02935d6875d0d217a0c606893491b3f240acd53544f32a86292fdeb46e4852965cd50f694d43cabb471ea', 'patient', NULL, 'P0018', '7845487851', NULL, NULL, 'Free', NULL, '2026-03-23 06:31:44', NULL),
(20, 'vyshnavi', 'vyshnavinarala12@gmail.com', 'scrypt:32768:8:1$uOUj7AxucvrDoEwm$f6754eef36702a2b103b34aedbe46ba1dfad7fbdc06a5b519a57755c7e2851ea5a8cca59df23013cb36a4f9f491442a2f346f30b3a20c62e269865055fc24acb', 'dentist', 'D3311', '', NULL, NULL, NULL, 'Free', NULL, '2026-03-24 08:42:28', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `reports`
--

CREATE TABLE `reports` (
  `id` int(11) NOT NULL,
  `case_id` int(11) NOT NULL,
  `deficiency_addressed` text DEFAULT NULL,
  `ai_reasoning` text DEFAULT NULL,
  `risk_analysis` text DEFAULT NULL,
  `aesthetic_prognosis` text DEFAULT NULL,
  `placement_strategy` text DEFAULT NULL,
  `final_recommendation` text DEFAULT NULL,
  `hyperdontia_status` varchar(50) DEFAULT NULL,
  `aesthetic_symmetry` varchar(50) DEFAULT NULL,
  `golden_ratio` varchar(50) DEFAULT NULL,
  `missing_teeth_status` varchar(50) DEFAULT NULL,
  `medications` text DEFAULT NULL,
  `care_instructions` text DEFAULT NULL,
  `created_at` timestamp NOT NULL DEFAULT current_timestamp(),
  `suggested_restoration` varchar(255) DEFAULT NULL,
  `suggested_material` varchar(255) DEFAULT NULL,
  `redness_analysis` varchar(255) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `reports`
--

INSERT INTO `reports` (`id`, `case_id`, `deficiency_addressed`, `ai_reasoning`, `risk_analysis`, `aesthetic_prognosis`, `placement_strategy`, `final_recommendation`, `hyperdontia_status`, `aesthetic_symmetry`, `golden_ratio`, `missing_teeth_status`, `medications`, `care_instructions`, `created_at`, `suggested_restoration`, `suggested_material`, `redness_analysis`) VALUES
(26, 62, 'Healthy', 'Clinical analysis indicates healthy dental structure with 80.2% confidence.', 'Low clinical risk identified.', 'Stable outlook with regular monitoring.', 'Standard clinical protocol suggested.', 'N/A', 'None', 'Optimal', '1.618 Match', 'None', 'No medications prescribed.', 'Standard oral hygiene maintenance suggested.', '2026-03-25 07:18:53', NULL, NULL, NULL);

--
-- Indexes for dumped tables
--

--
-- Indexes for table `appointments`
--
ALTER TABLE `appointments`
  ADD PRIMARY KEY (`id`),
  ADD KEY `case_id` (`case_id`),
  ADD KEY `dentist_id` (`dentist_id`);

--
-- Indexes for table `care_tips`
--
ALTER TABLE `care_tips`
  ADD PRIMARY KEY (`id`),
  ADD KEY `case_id` (`case_id`);

--
-- Indexes for table `cases`
--
ALTER TABLE `cases`
  ADD PRIMARY KEY (`id`),
  ADD KEY `dentist_id` (`dentist_id`);

--
-- Indexes for table `case_files`
--
ALTER TABLE `case_files`
  ADD PRIMARY KEY (`id`),
  ADD KEY `case_id` (`case_id`);

--
-- Indexes for table `case_timeline`
--
ALTER TABLE `case_timeline`
  ADD PRIMARY KEY (`id`),
  ADD KEY `case_id` (`case_id`);

--
-- Indexes for table `dentist_profiles`
--
ALTER TABLE `dentist_profiles`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `dentist_id` (`dentist_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `healing_logs`
--
ALTER TABLE `healing_logs`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `medications`
--
ALTER TABLE `medications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `case_id` (`case_id`);

--
-- Indexes for table `notifications`
--
ALTER TABLE `notifications`
  ADD PRIMARY KEY (`id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `register`
--
ALTER TABLE `register`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `email` (`email`),
  ADD UNIQUE KEY `patient_id` (`patient_id`),
  ADD UNIQUE KEY `dentist_id` (`dentist_id`);

--
-- Indexes for table `reports`
--
ALTER TABLE `reports`
  ADD PRIMARY KEY (`id`),
  ADD KEY `case_id` (`case_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `appointments`
--
ALTER TABLE `appointments`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `care_tips`
--
ALTER TABLE `care_tips`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `cases`
--
ALTER TABLE `cases`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=63;

--
-- AUTO_INCREMENT for table `case_files`
--
ALTER TABLE `case_files`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=125;

--
-- AUTO_INCREMENT for table `case_timeline`
--
ALTER TABLE `case_timeline`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `dentist_profiles`
--
ALTER TABLE `dentist_profiles`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `healing_logs`
--
ALTER TABLE `healing_logs`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `medications`
--
ALTER TABLE `medications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT;

--
-- AUTO_INCREMENT for table `notifications`
--
ALTER TABLE `notifications`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=3;

--
-- AUTO_INCREMENT for table `register`
--
ALTER TABLE `register`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=21;

--
-- AUTO_INCREMENT for table `reports`
--
ALTER TABLE `reports`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=27;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `appointments`
--
ALTER TABLE `appointments`
  ADD CONSTRAINT `appointments_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`) ON DELETE CASCADE,
  ADD CONSTRAINT `appointments_ibfk_2` FOREIGN KEY (`dentist_id`) REFERENCES `register` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `care_tips`
--
ALTER TABLE `care_tips`
  ADD CONSTRAINT `care_tips_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `cases`
--
ALTER TABLE `cases`
  ADD CONSTRAINT `cases_ibfk_1` FOREIGN KEY (`dentist_id`) REFERENCES `register` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `case_files`
--
ALTER TABLE `case_files`
  ADD CONSTRAINT `case_files_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `case_timeline`
--
ALTER TABLE `case_timeline`
  ADD CONSTRAINT `case_timeline_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `dentist_profiles`
--
ALTER TABLE `dentist_profiles`
  ADD CONSTRAINT `dentist_profiles_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `register` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `medications`
--
ALTER TABLE `medications`
  ADD CONSTRAINT `medications_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `notifications`
--
ALTER TABLE `notifications`
  ADD CONSTRAINT `notifications_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `register` (`id`) ON DELETE CASCADE;

--
-- Constraints for table `reports`
--
ALTER TABLE `reports`
  ADD CONSTRAINT `reports_ibfk_1` FOREIGN KEY (`case_id`) REFERENCES `cases` (`id`) ON DELETE CASCADE;
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
