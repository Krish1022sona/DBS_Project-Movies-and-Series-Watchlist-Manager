CREATE DATABASE Streamsync;

use Streamsync ;

CREATE TABLE Users (
    username varchar(50) unique primary key,
    firstname varchar(50) not null,
    lastname varchar(50),
    DOB date not null,
    email VARCHAR(255) NOT NULL UNIQUE,
    CHECK (
        email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
    ),
    password char(64) NOT NULL, -- while insertion of data use SHA2('password',256) similar to bcrypt but less secure
    role ENUM('user', 'admin', 'moderator') DEFAULT 'user',
    created_at datetime DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Media (
    media_id varchar(10) primary key,
    title varchar(100) NOT NULL,
    description TEXT COMMENT 'details about media',
    release_year YEAR,
    media_type varchar(20),
    check (
        media_type IN ('Movie', 'Series')
    ),
    age_rating ENUM(
        'G',
        'PG',
        'PG-13',
        'NC-17',
        'U',
        'U/A 7+',
        'U/A 13+',
        'U/A 16+',
        'A'
    ) DEFAULT 'U',
    poster_image_url varchar(2083),
    average_rating DECIMAL(3, 1)
);

CREATE TABLE genres (
    genre_id varchar(50) PRIMARY KEY,
    name varchar(50) NOT NULL
);

CREATE TABLE Episodes (
    episode_id VARCHAR(50) PRIMARY KEY,
    media_id varchar(10) NOT NULL,
    season_number INT,
    episode_number INT,
    title VARCHAR(100),
    air_date DATE,
    UNIQUE (
        media_id,
        season_number,
        episode_number
    ), -- prevents duplicate episodes
    FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Watchlists_item (
    username varchar(50) NOT NULL,
    media_id varchar(10) NOT NULL,
    status VARCHAR(20) CHECK (
        status IN (
            'watching',
            'completed',
            'planned',
            'dropped'
        )
    ),
    user_rating INT CHECK (user_rating BETWEEN 1 AND 10),
    PRIMARY KEY (username, media_id),
    FOREIGN KEY (username) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE playlist (
    playlist_id varchar(20) PRIMARY KEY,
    username varchar(50) NOT NULL,
    name varchar(30),
    created_at datetime DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Playlist_item (
    playlist_id varchar(20) NOT NULL,
    media_id varchar(10) NOT NULL,
    PRIMARY KEY (playlist_id, media_id),
    FOREIGN KEY (playlist_id) REFERENCES Playlist (playlist_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Media_Genres (
    media_id varchar(10) NOT NULL,
    genre_id varchar(50) NOT NULL,
    PRIMARY KEY (media_id, genre_id),
    FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genres (genre_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Series_Progress_Table (
    username varchar(50) NOT NULL,
    media_id varchar(10) NOT NULL,
    last_watched_episode_id VARCHAR(50),
    last_watched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username, media_id),
    FOREIGN KEY (username) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (last_watched_episode_id) REFERENCES Episodes (episode_id)
);

CREATE TABLE Reviews_Table (
    review_id varchar(10) PRIMARY KEY,
    username varchar(50) NOT NULL,
    media_id varchar(10) NOT NULL,
    review_text TEXT,
    rating INT CHECK (rating BETWEEN 1 AND 10) created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Friends (
    username_1 varchar(50) NOT NULL,
    username_2 varchar(50) NOT NULL,
    status varchar(15),
    check (
        status IN (
            'pending',
            'accepted',
            'blocked'
        )
    ),
    created_at datetime DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (username_1, username_2),
    FOREIGN KEY (username_1) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (username_2) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE People (
    person_id varchar(20) primary key,
    name varchar(40),
    birthdate date,
    photo_url varchar(2083)
);

CREATE TABLE Media_Cast (
    media_id varchar(10) NOT NULL,
    person_id varchar(20) NOT NULL,
    character_name VARCHAR(100),
    PRIMARY KEY (media_id, person_id),
    FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (person_id) REFERENCES People (person_id) ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Media_Crew (
    media_id varchar(10) NOT NULL,
    person_id varchar(20) NOT NULL,
    role VARCHAR(50),
    PRIMARY KEY (media_id, person_id, role),
    FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (person_id) REFERENCES People (person_id) ON DELETE CASCADE ON UPDATE CASCADE
);
-- adding indexs for foreign keys

CREATE INDEX idx_media_id ON Episodes (media_id);

CREATE INDEX idx_username ON Watchlists_item (username);

CREATE INDEX idx_media_genre ON Media_Genres (media_id, genre_id);

CREATE INDEX idx_user_media ON Series_Progress_Table (username, media_id);

CREATE INDEX idx_genre_id ON Media_Genres (genre_id);

CREATE TABLE Activity_Log (
    log_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50), -- who changed
    table_name VARCHAR(50), -- in which table change made
    operation ENUM('INSERT', 'UPDATE', 'DELETE'), -- which operation
    record_id VARCHAR(100), -- in which record
    change_details TEXT, --  what changed
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
-- triggers
CREATE TRIGGER after_media_insert
AFTER INSERT ON Media
FOR EACH ROW
INSERT INTO Activity_Log (username, table_name, operation, record_id, change_details)
VALUES (CURRENT_USER(), 'Media', 'INSERT', NEW.media_id, CONCAT('Added media: ', NEW.title));

CREATE TRIGGER after_media_delete
AFTER DELETE ON Media
FOR EACH ROW
INSERT INTO Activity_Log (username, table_name, operation, record_id, change_details)
VALUES (CURRENT_USER(), 'Media', 'DELETE', OLD.media_id, CONCAT('Deleted media: ', OLD.title));

CREATE TRIGGER after_media_update
AFTER UPDATE ON Media
FOR EACH ROW
INSERT INTO Activity_Log (username, table_name, operation, record_id, change_details)
VALUES (CURRENT_USER(), 'Media', 'UPDATE', NEW.media_id, CONCAT('Updated media: ', NEW.title));

-- review table triggers

DELIMITER $$
CREATE TRIGGER after_review_insert
AFTER INSERT ON Reviews_Table
for each row
BEGIN
    UPDATE Media
    SET average_rating = (
        SELECT ROUND(AVG(rating), 1)
        FROM Reviews_Table
        WHERE media_id = NEW.media_id
    )
    WHERE media_id = NEW.media_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER after_review_update
AFTER UPDATE ON Reviews_Table
for each row
BEGIN
    UPDATE Media
    SET average_rating = (
        SELECT ROUND(AVG(rating), 1)
        FROM Reviews_Table
        WHERE media_id = NEW.media_id
    )
    WHERE media_id = NEW.media_id;
END$$
DELIMITER ;

DELIMITER $$
CREATE TRIGGER after_review_delete
AFTER DELETE ON Reviews_Table
for each row
BEGIN
    UPDATE Media
    SET average_rating = (
        SELECT 
            case
                WHEN COUNT(*) = 0 THEN NULL
                ELSE ROUND(AVG(rating), 1)
		    end
        from Reviews_Table
        WHERE media_id = OLD.media_id
    )
    WHERE media_id = OLD.media_id;
END$$
DELIMITER ;

SELECT * FROM Activity_Log ORDER BY changed_at DESC;