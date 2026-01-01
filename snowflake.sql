CREATE OR REPLACE WAREHOUSE inspection_wh
WITH WAREHOUSE_SIZE = 'XSMALL'
AUTO_SUSPEND = 300
AUTO_RESUME = TRUE;

CREATE DATABASE inspection_db;
USE DATABASE inspection_db;

CREATE SCHEMA inspection_schema;
USE SCHEMA inspection_schema;

-- Properties table
CREATE TABLE properties (
    property_id INT AUTOINCREMENT PRIMARY KEY,
    property_name STRING,
    address STRING
);

-- Rooms table
CREATE TABLE rooms (
    room_id INT AUTOINCREMENT PRIMARY KEY,
    property_id INT,
    room_name STRING,
    FOREIGN KEY(property_id) REFERENCES properties(property_id)
);

-- Inspection findings table
CREATE TABLE inspection_findings (
    finding_id INT AUTOINCREMENT PRIMARY KEY,
    property_id INT,
    room_id INT,
    note_text STRING,
    issue_type STRING, -- 'crack', 'damp', 'leak', 'ok'
    severity STRING,   -- 'critical', 'moderate', 'low'
    inspection_date DATE DEFAULT CURRENT_DATE(),
    FOREIGN KEY(property_id) REFERENCES properties(property_id),
    FOREIGN KEY(room_id) REFERENCES rooms(room_id)
);

-- Optional: Image metadata table
CREATE TABLE image_metadata (
    image_id INT AUTOINCREMENT PRIMARY KEY,
    property_id INT,
    room_id INT,
    file_name STRING,
    label STRING -- manually labelled: 'crack', 'leak', 'ok'
);

--insertion

-- Properties
INSERT INTO properties (property_name, address) VALUES 
('Sunrise Apartments', '123 Main St'), 
('Green Villa', '456 Oak Rd');

-- Rooms
INSERT INTO rooms (property_id, room_name) VALUES 
(1, 'Living Room'), (1, 'Kitchen'), (1, 'Bedroom'),
(2, 'Living Room'), (2, 'Bathroom');

-- Inspection findings
INSERT INTO inspection_findings (property_id, room_id, note_text, issue_type, severity) VALUES
(1, 1, 'Small crack near window', 'crack', 'moderate'),
(1, 2, 'Damp wall behind sink', 'damp', 'critical'),
(1, 3, 'No issues', 'ok', 'low'),
(2, 1, 'Leaking pipe', 'leak', 'critical'),
(2, 2, 'Floor ok', 'ok', 'low');


--create riskscore table

CREATE TABLE risk_scores (
    property_id INT PRIMARY KEY,
    risk_score FLOAT
);

--Create Stream & Task for Auto-Risk Updates

CREATE STREAM inspection_findings_stream
ON TABLE inspection_findings
SHOW_INITIAL_ROWS = TRUE;

CREATE TASK update_risk_score_task
WAREHOUSE = inspection_wh
SCHEDULE = 'USING CRON 0 * * * * UTC'  -- runs at the start of every hour in UTC
AS
MERGE INTO risk_scores AS r
USING (
    SELECT 
        property_id,
        (SUM(CASE WHEN severity='critical' THEN 3
                  WHEN severity='moderate' THEN 2
                  ELSE 1 END) / COUNT(*)) AS risk_score
    FROM inspection_findings
    GROUP BY property_id
) AS s
ON r.property_id = s.property_id
WHEN MATCHED THEN UPDATE SET r.risk_score = s.risk_score
WHEN NOT MATCHED THEN INSERT (property_id, risk_score) VALUES (s.property_id, s.risk_score);


ALTER WAREHOUSE inspection_wh RESUME;

CREATE OR REPLACE TABLE inspection_findings (
    finding_id INTEGER AUTOINCREMENT,
    note_text STRING
);

INSERT INTO inspection_findings (note_text) VALUES
('Crack found in main beam near entrance'),
('Water leakage and dampness on ceiling'),
('Exposed electrical wiring near panel'),
('Fire extinguisher missing on floor 2'),
('Minor paint damage observed');
