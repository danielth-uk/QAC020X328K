CREATE TABLE `tbl_users` (
  `userid` varchar(64) NOT NULL,
  `org` varchar(32) NOT NULL,
  `username` varchar(32) NOT NULL,
  `password` varchar(256) NOT NULL,
  `clear_password` varchar(256) NOT NULL,
  `admin` tinyint(1) NOT NULL,
  `name` varchar(64) NOT NULL,
  `token` varchar(256) NULL,
  PRIMARY KEY (userid)
) ENGINE=InnoDB COLLATE=utf8mb4_general_ci;

CREATE TABLE `tbl_tickets` (
  `id` int NOT NULL AUTO_INCREMENT,
  `subject` varchar(16) DEFAULT NULL,
  `created_by` varchar(64) NOT NULL,
  `assigned_contact` varchar(64) NULL,
  `org` text NOT NULL,
  `tags` varchar(64) NULL,
  `opened_time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `last_message` datetime NULL,
  `main_body` JSON,
  `closed` tinyint(1) DEFAULT 0,
  PRIMARY KEY (id),
  FOREIGN KEY (created_by) REFERENCES tbl_users(userid),
  FOREIGN KEY (assigned_contact) REFERENCES tbl_users(userid)
) ENGINE=InnoDB COLLATE=utf8mb4_general_ci;

CREATE TABLE `tbl_ticket_comments` (
  `id` int NOT NULL AUTO_INCREMENT,
  `ticket_id` int NOT NULL,
  `comment_body` JSON,
  `posted` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `posted_by` varchar(64),
  `updated` tinyint(1) NOT NULL DEFAULT '0',
  PRIMARY KEY (id),
  FOREIGN KEY (ticket_id) REFERENCES tbl_tickets(id),
  FOREIGN KEY (posted_by) REFERENCES tbl_users(userid)
) ENGINE=InnoDB COLLATE=utf8mb4_general_ci;


-- Importing data

INSERT INTO `tbl_users` (`userid`, `org`, `username`, `password`,`clear_password`, `admin`, `name`) VALUES
('test.user', 'test', 'user','99ea56ced47c21431d0c56ef904f282ae4256adb612c4e890b6daa1b61d0c32c', 'cGFzc3dvcmQ=', 0, 'Testing User'),
('test.admin', 'test', 'admin','99ea56ced47c21431d0c56ef904f282ae4256adb612c4e890b6daa1b61d0c32c', 'cGFzc3dvcmQ=', 1, 'Testing Admin')

INSERT INTO `tbl_tickets` (`id`, `subject`, `created_by`, `assigned_contact`, `org`, `tags`, `opened_time`, `last_message`, `main_body`, `closed`) VALUES
	(1, 'Lorem Ipsum', 'test.user', 'test.admin', 'test', 'Lorem, Ipsum', '2023-06-07 12:40:07', NULL, '[{"insert": "Lorem Ipsum"}, {"insert": "\\\\n", "attributes": {"header": 1}}, {"insert": "\\\\n"}, {"insert": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur", "attributes": {"color": "#444444", "background": "#ff9900"}}, {"insert": "\\\\n"}]', 0),
	(2, 'Lorem Ipsum 2', 'test.user', 'test.admin', 'test', 'Ipsum, Lorem', '2023-06-07 12:34:45', NULL, '[{"insert": "test\\\\n"}]', 0);

INSERT INTO `tbl_ticket_comments` (`id`, `ticket_id`, `comment_body`, `posted`, `posted_by`, `updated`) VALUES
	(1, 1, '[{"insert": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur", "attributes": {"bold": true, "italic": true}}, {"insert": "\\\\n"}]', '2023-06-07 12:40:30', 'test.user', 0),
	(2, 1, '[{"insert": "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur", "attributes": {"bold": true, "italic": true}}, {"insert": "\\\\n"}]', '2023-06-07 12:43:17', 'test.admin', 0);
