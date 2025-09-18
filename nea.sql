-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Host: 127.0.0.1
-- Generation Time: Apr 06, 2025 at 11:24 PM
-- Server version: 10.4.32-MariaDB
-- PHP Version: 8.0.30

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `nea`
--

-- --------------------------------------------------------

--
-- Table structure for table `availability`
--

CREATE TABLE `availability` (
  `id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `day` varchar(20) NOT NULL,
  `hours` longtext CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL CHECK (json_valid(`hours`))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `availability`
--

INSERT INTO `availability` (`id`, `user_id`, `day`, `hours`) VALUES
(101, 5, 'Monday', '19'),
(102, 5, 'Tuesday', NULL),
(103, 5, 'Wednesday', NULL),
(104, 5, 'Thursday', NULL),
(105, 5, 'Friday', NULL),
(106, 5, 'Saturday', NULL),
(107, 5, 'Sunday', NULL),
(109, 6, 'Monday', NULL),
(110, 6, 'Tuesday', NULL),
(111, 6, 'Wednesday', NULL),
(112, 6, 'Thursday', NULL),
(113, 6, 'Friday', NULL),
(114, 6, 'Saturday', NULL),
(115, 6, 'Sunday', NULL),
(118, 9, 'Monday', NULL),
(119, 9, 'Tuesday', NULL),
(120, 9, 'Wednesday', NULL),
(121, 9, 'Thursday', NULL),
(122, 9, 'Friday', NULL),
(123, 9, 'Saturday', NULL),
(124, 9, 'Sunday', NULL);

-- --------------------------------------------------------

--
-- Table structure for table `events`
--

CREATE TABLE `events` (
  `user_id` int(11) NOT NULL,
  `date` text NOT NULL,
  `time` text NOT NULL,
  `title` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `events`
--

INSERT INTO `events` (`user_id`, `date`, `time`, `title`) VALUES
(5, '2025-03-10', '19:00:00', 'ki'),
(6, '2025-03-14', '12:00:00', 'finish nea'),
(7, '2025-04-01', '21:00:00', 'pay gorn'),
(1, '2025-03-31', '00:00:00', 'Math'),
(1, '2025-04-01', '12:00:00', 'Math'),
(1, '2025-04-01', '13:00:00', 'Math'),
(1, '2025-04-02', '09:00:00', 'Science'),
(1, '2025-04-02', '10:00:00', 'Science'),
(1, '2025-04-02', '11:00:00', 'Science'),
(1, '2025-04-03', '00:00:00', 'Math'),
(1, '2025-04-03', '01:00:00', 'Math'),
(1, '2025-04-03', '02:00:00', 'Math'),
(1, '2025-04-03', '03:00:00', 'Math'),
(1, '2025-04-03', '04:00:00', 'Math'),
(1, '2025-04-03', '05:00:00', 'Math'),
(1, '2025-04-03', '06:00:00', 'Math'),
(1, '2025-04-03', '07:00:00', 'Math'),
(1, '2025-04-03', '08:00:00', 'Science'),
(1, '2025-04-03', '09:00:00', 'Science'),
(1, '2025-04-03', '10:00:00', 'Science'),
(1, '2025-04-04', '22:00:00', 'Science'),
(1, '2025-04-05', '12:00:00', 'Science'),
(1, '2025-04-05', '13:00:00', 'Science'),
(1, '2025-04-06', '12:00:00', 'Science');

-- --------------------------------------------------------

--
-- Table structure for table `flashcards`
--

CREATE TABLE `flashcards` (
  `card_id` int(11) NOT NULL,
  `subject_id` int(11) NOT NULL,
  `user_id` int(11) NOT NULL,
  `front` text NOT NULL,
  `back` text NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `flashcards`
--

INSERT INTO `flashcards` (`card_id`, `subject_id`, `user_id`, `front`, `back`) VALUES
(4, 1, 1, 'What is 2+2?', '4'),
(6, 2, 1, 'What is H2O?', 'Water'),
(37, 3, 1, 'nano-material', 'really small materials that are man made'),
(38, 1, 1, '3-2', '1'),
(39, 1, 1, 'd', 'a'),
(40, 1, 1, '9-8', '2'),
(41, 1, 1, 'tersting', 'yh'),
(42, 3, 1, 'smart material', 'a material that changes depending on the enviroment'),
(43, 28, 5, 'saim', 'hi shadosme'),
(44, 1, 1, '3+4', '7'),
(45, 1, 1, '4-5', '-1'),
(46, 33, 7, 'gooning', 'one who masturbayes'),
(47, 33, 7, 'edging', 'to edge the cuim');

-- --------------------------------------------------------

--
-- Table structure for table `scores`
--

CREATE TABLE `scores` (
  `subject_id` int(11) DEFAULT NULL,
  `month` int(11) DEFAULT NULL CHECK (`month` between 1 and 12),
  `year` int(11) DEFAULT NULL,
  `score` float DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `scores`
--

INSERT INTO `scores` (`subject_id`, `month`, `year`, `score`) VALUES
(1, 1, 2023, 85.5),
(1, 2, 2023, 87),
(2, 1, 2023, 90),
(2, 2, 2023, 88.5),
(28, 1, 2025, 90),
(1, 1, 2026, 40),
(1, 2, 2026, 90),
(1, 3, 2026, 30);

-- --------------------------------------------------------

--
-- Table structure for table `subjects`
--

CREATE TABLE `subjects` (
  `subject_id` int(11) NOT NULL,
  `user_id` int(11) DEFAULT NULL,
  `subject_name` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `subjects`
--

INSERT INTO `subjects` (`subject_id`, `user_id`, `subject_name`) VALUES
(1, 1, 'Math'),
(2, 1, 'Science'),
(3, 1, 'TECh'),
(28, 5, 'ki'),
(29, 6, 'tech'),
(30, 6, 'science'),
(31, 6, 'math'),
(32, 5, 'math'),
(33, 7, 'masturbation'),
(34, 9, 'lo');

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE `users` (
  `user_id` int(11) NOT NULL,
  `username` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Dumping data for table `users`
--

INSERT INTO `users` (`user_id`, `username`, `password`) VALUES
(1, 'saim', '1234'),
(3, 'hilman', '1234'),
(4, 'mahi', '1234'),
(5, 'link', '1234'),
(6, 'hilly', 'shit'),
(7, 'dick', 'pussy'),
(8, 'somehting', 'nioo'),
(9, 'lol_', 'lolo');

--
-- Indexes for dumped tables
--

--
-- Indexes for table `availability`
--
ALTER TABLE `availability`
  ADD PRIMARY KEY (`id`),
  ADD UNIQUE KEY `unique_user_day` (`user_id`,`day`);

--
-- Indexes for table `events`
--
ALTER TABLE `events`
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `flashcards`
--
ALTER TABLE `flashcards`
  ADD PRIMARY KEY (`card_id`),
  ADD KEY `subject_id` (`subject_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `scores`
--
ALTER TABLE `scores`
  ADD KEY `subject_id` (`subject_id`);

--
-- Indexes for table `subjects`
--
ALTER TABLE `subjects`
  ADD PRIMARY KEY (`subject_id`),
  ADD KEY `user_id` (`user_id`);

--
-- Indexes for table `users`
--
ALTER TABLE `users`
  ADD PRIMARY KEY (`user_id`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `availability`
--
ALTER TABLE `availability`
  MODIFY `id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=125;

--
-- AUTO_INCREMENT for table `flashcards`
--
ALTER TABLE `flashcards`
  MODIFY `card_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=48;

--
-- AUTO_INCREMENT for table `subjects`
--
ALTER TABLE `subjects`
  MODIFY `subject_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=35;

--
-- AUTO_INCREMENT for table `users`
--
ALTER TABLE `users`
  MODIFY `user_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=10;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `availability`
--
ALTER TABLE `availability`
  ADD CONSTRAINT `availability_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `events`
--
ALTER TABLE `events`
  ADD CONSTRAINT `events_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);

--
-- Constraints for table `flashcards`
--
ALTER TABLE `flashcards`
  ADD CONSTRAINT `flashcards_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`subject_id`) ON DELETE CASCADE,
  ADD CONSTRAINT `flashcards_ibfk_2` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`) ON DELETE CASCADE;

--
-- Constraints for table `scores`
--
ALTER TABLE `scores`
  ADD CONSTRAINT `scores_ibfk_1` FOREIGN KEY (`subject_id`) REFERENCES `subjects` (`subject_id`);

--
-- Constraints for table `subjects`
--
ALTER TABLE `subjects`
  ADD CONSTRAINT `subjects_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `users` (`user_id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
