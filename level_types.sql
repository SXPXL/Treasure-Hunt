-- Table to store the type for each level (set by admin)
CREATE TABLE IF NOT EXISTS level_types (
    level INT PRIMARY KEY,
    type VARCHAR(32) NOT NULL
);
