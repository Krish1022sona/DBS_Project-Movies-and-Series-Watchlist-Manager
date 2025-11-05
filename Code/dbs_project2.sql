CREATE DATABASE p1;
use p1;
CREATE TABLE Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username varchar(50),
    email VARCHAR(255) NOT NULL UNIQUE,
    CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    password varbinary(64) NOT NULL ,   -- while insertion of data use SHA2('password',256) similar to bcrypt but less secure
    created_at datetime DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE Media(
media_id INT AUTO_INCREMENT primary key,
title varchar(100) NOT NULL,
description TEXT COMMENT 'details about media',
release_year YEAR,
media_type varchar(20),
  check(media_type IN ('Movie','Series')),
  poster_image_url varchar(2083),
  average_rating float
);
CREATE TABLE genres(
genre_id varchar(50) PRIMARY KEY,
name varchar(50) NOT NULL
);
CREATE TABLE Episodes(
  episode_id VARCHAR(50) PRIMARY KEY,
    media_id INT NOT NULL,
    season_number INT,
    episode_number INT,
    title VARCHAR(100),
    air_date DATE,
    FOREIGN KEY (media_id) REFERENCES Media(media_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE Watchlists_item(
  user_id INT NOT NULL,
    media_id INT NOT NULL,
    status VARCHAR(20) CHECK (status IN ('watching','completed','planned','dropped')),
    user_rating INT CHECK (user_rating BETWEEN 1 AND 10),
    PRIMARY KEY (user_id, media_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (media_id) REFERENCES Media(media_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE playlist(
playlist_id INT AUTO_INCREMENT PRIMARY KEY,
user_id INT  NOT NULL,
name varchar(30),
created_at datetime DEFAULT CURRENT_TIMESTAMP,
 FOREIGN KEY (user_id) REFERENCES Users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE Playlist_item(
playlist_id INT NOT NULL,
media_id INT NOT NULL,
PRIMARY KEY (playlist_id, media_id),
    FOREIGN KEY (playlist_id) REFERENCES Playlist(playlist_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (media_id) REFERENCES Media(media_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE Media_Genres(
media_id INT NOT NULL,
genre_id varchar(50) NOT NULL,
PRIMARY KEY (media_id, genre_id),
    FOREIGN KEY (media_id) REFERENCES Media(media_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (genre_id) REFERENCES Genres(genre_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE  Series_Progress_Table(
user_id INT NOT NULL,
    media_id INT NOT NULL,
    last_watched_episode_id VARCHAR(50),
    last_watched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id, media_id),
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (media_id) REFERENCES Media(media_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (last_watched_episode_id) REFERENCES Episodes(episode_id)
);
CREATE TABLE Reviews_Table(
 review_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    media_id INT NOT NULL,
    review_text TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (media_id) REFERENCES Media(media_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE Friends(
user_id_1 INT NOT NULL,
user_id_2 INT NOT NULL,
status varchar(15),
 check(status IN ('pending','accepted','blocked')),
 created_at datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (user_id_1, user_id_2),
    FOREIGN KEY (user_id_1) REFERENCES Users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (user_id_2) REFERENCES Users(user_id)
    ON DELETE CASCADE ON UPDATE CASCADE
 
);
CREATE TABLE People(
person_id INT  AUTO_INCREMENT primary key,
name varchar(40),
birthdate date,
photo_url varchar(2083)
);
CREATE TABLE Media_Cast (
    media_id INT NOT NULL,
    person_id INT NOT NULL,
    character_name VARCHAR(100),
    PRIMARY KEY (media_id, person_id),
    FOREIGN KEY (media_id) REFERENCES Media(media_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (person_id) REFERENCES People(person_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);
CREATE TABLE Media_Crew (
    media_id INT NOT NULL,
    person_id INT NOT NULL,
    role VARCHAR(50),
    PRIMARY KEY (media_id, person_id, role),
    FOREIGN KEY (media_id) REFERENCES Media(media_id)
    ON DELETE CASCADE ON UPDATE CASCADE,
    FOREIGN KEY (person_id) REFERENCES People(person_id)
    ON DELETE CASCADE ON UPDATE CASCADE
);



 

