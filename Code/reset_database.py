import mysql.connector
from mysql.connector import Error
import toml
import os
from datetime import datetime, date

def load_secrets():
    """Load database credentials - hardcoded"""
    return {
        'host': 'localhost',
        'user': 'root',
        'password': 'Krishnasona',
        'database': 'Streamsync'
    }

def get_connection(use_database=False):
    """Get database connection"""
    db_config = load_secrets()
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            user=db_config['user'],
            password=db_config['password']
        )
        if use_database:
            cursor = conn.cursor()
            cursor.execute(f"USE {db_config['database']}")
            cursor.close()
        return conn
    except Error as e:
        print(f"Connection error: {e}")
        return None

def reset_database():
    """Drop and recreate the database"""
    conn = get_connection()
    if not conn:
        return False
    
    db_config = load_secrets()
    cursor = conn.cursor()
    
    try:
        print("Dropping existing database...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_config['database']}")
        print("Creating new database...")
        cursor.execute(f"CREATE DATABASE {db_config['database']}")
        cursor.execute(f"USE {db_config['database']}")
        conn.commit()
        print("Database reset successful!")
        return True
    except Error as e:
        print(f"Error resetting database: {e}")
        return False
    finally:
        cursor.close()

def create_tables(conn):
    """Create all tables"""
    cursor = conn.cursor()
    
    tables = [
        """CREATE TABLE Users (
            username varchar(50) unique primary key,
            firstname varchar(50) not null,
            lastname varchar(50),
            DOB date not null,
            email VARCHAR(255) NOT NULL UNIQUE,
            CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),
            password char(64) NOT NULL,
            role ENUM('user', 'admin', 'moderator') DEFAULT 'user',
            created_at datetime DEFAULT CURRENT_TIMESTAMP
        )""",
        
        """CREATE TABLE Media (
            media_id varchar(10) primary key,
            title varchar(100) NOT NULL,
            description TEXT,
            release_year YEAR,
            media_type varchar(20),
            check (media_type IN ('Movie', 'Series')),
            age_rating ENUM('G','PG','PG-13','NC-17','U','U/A 7+','U/A 13+','U/A 16+','A') DEFAULT 'U',
            poster_image_url varchar(2083),
            average_rating DECIMAL(3, 1)
        )""",
        
        """CREATE TABLE genres (
            genre_id varchar(50) PRIMARY KEY,
            name varchar(50) NOT NULL
        )""",
        
        """CREATE TABLE People (
            person_id varchar(20) primary key,
            name varchar(40),
            birthdate date,
            photo_url varchar(2083)
        )""",
        
        """CREATE TABLE Episodes (
            episode_id VARCHAR(50) PRIMARY KEY,
            media_id varchar(10) NOT NULL,
            season_number INT,
            episode_number INT,
            title VARCHAR(100),
            air_date DATE,
            UNIQUE (media_id, season_number, episode_number),
            FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE
        )""",
        
        """CREATE TABLE Watchlists_item (
            username varchar(50) NOT NULL,
            media_id varchar(10) NOT NULL,
            status VARCHAR(20) CHECK (status IN ('watching', 'completed', 'planned', 'dropped')),
            user_rating INT CHECK (user_rating BETWEEN 1 AND 10),
            PRIMARY KEY (username, media_id),
            FOREIGN KEY (username) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE
        )""",
        
        """CREATE TABLE playlist (
            playlist_id varchar(20) PRIMARY KEY,
            username varchar(50) NOT NULL,
            name varchar(30),
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE
        )""",
        
        """CREATE TABLE Playlist_item (
            playlist_id varchar(20) NOT NULL,
            media_id varchar(10) NOT NULL,
            PRIMARY KEY (playlist_id, media_id),
            FOREIGN KEY (playlist_id) REFERENCES playlist (playlist_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE
        )""",
        
        """CREATE TABLE Media_Genres (
            media_id varchar(10) NOT NULL,
            genre_id varchar(50) NOT NULL,
            PRIMARY KEY (media_id, genre_id),
            FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (genre_id) REFERENCES genres (genre_id) ON DELETE CASCADE ON UPDATE CASCADE
        )""",
        
        """CREATE TABLE Series_Progress_Table (
            username varchar(50) NOT NULL,
            media_id varchar(10) NOT NULL,
            last_watched_episode_id VARCHAR(50),
            last_watched_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (username, media_id),
            FOREIGN KEY (username) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (last_watched_episode_id) REFERENCES Episodes (episode_id)
        )""",
        
        """CREATE TABLE Reviews_Table (
            review_id varchar(10) PRIMARY KEY,
            username varchar(50) NOT NULL,
            media_id varchar(10) NOT NULL,
            review_text TEXT,
            rating INT CHECK (rating BETWEEN 1 AND 10),
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE
        )""",
        
        """CREATE TABLE Friends (
            username_1 varchar(50) NOT NULL,
            username_2 varchar(50) NOT NULL,
            status varchar(15),
            check (status IN ('pending', 'accepted', 'blocked')),
            created_at datetime DEFAULT CURRENT_TIMESTAMP,
            PRIMARY KEY (username_1, username_2),
            FOREIGN KEY (username_1) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (username_2) REFERENCES Users (username) ON DELETE CASCADE ON UPDATE CASCADE
        )""",
        
        """CREATE TABLE Media_Cast (
            media_id varchar(10) NOT NULL,
            person_id varchar(20) NOT NULL,
            character_name VARCHAR(100),
            PRIMARY KEY (media_id, person_id),
            FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (person_id) REFERENCES People (person_id) ON DELETE CASCADE ON UPDATE CASCADE
        )""",
        
        """CREATE TABLE Media_Crew (
            media_id varchar(10) NOT NULL,
            person_id varchar(20) NOT NULL,
            role VARCHAR(50),
            PRIMARY KEY (media_id, person_id, role),
            FOREIGN KEY (media_id) REFERENCES Media (media_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (person_id) REFERENCES People (person_id) ON DELETE CASCADE ON UPDATE CASCADE
        )""",
        
        """CREATE TABLE Activity_Log (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            table_name VARCHAR(50),
            operation ENUM('INSERT', 'UPDATE', 'DELETE'),
            record_id VARCHAR(100),
            change_details TEXT,
            changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )"""
    ]
    
    print("Creating tables...")
    for table in tables:
        try:
            cursor.execute(table)
            print(f"  [OK] Created table")
        except Error as e:
            print(f"  [ERROR] Error creating table: {e}")
    
    indexes = [
        "CREATE INDEX idx_media_id ON Episodes (media_id)",
        "CREATE INDEX idx_username ON Watchlists_item (username)",
        "CREATE INDEX idx_media_genre ON Media_Genres (media_id, genre_id)",
        "CREATE INDEX idx_user_media ON Series_Progress_Table (username, media_id)",
        "CREATE INDEX idx_genre_id ON Media_Genres (genre_id)"
    ]
    
    print("Creating indexes...")
    for idx in indexes:
        try:
            cursor.execute(idx)
        except Error as e:
            print(f"  Index creation warning: {e}")
    
    triggers = [
        """CREATE TRIGGER after_media_insert
        AFTER INSERT ON Media
        FOR EACH ROW
        INSERT INTO Activity_Log (username, table_name, operation, record_id, change_details)
        VALUES (CURRENT_USER(), 'Media', 'INSERT', NEW.media_id, CONCAT('Added media: ', NEW.title))""",
        
        """CREATE TRIGGER after_media_delete
        AFTER DELETE ON Media
        FOR EACH ROW
        INSERT INTO Activity_Log (username, table_name, operation, record_id, change_details)
        VALUES (CURRENT_USER(), 'Media', 'DELETE', OLD.media_id, CONCAT('Deleted media: ', OLD.title))""",
        
        """CREATE TRIGGER after_media_update
        AFTER UPDATE ON Media
        FOR EACH ROW
        INSERT INTO Activity_Log (username, table_name, operation, record_id, change_details)
        VALUES (CURRENT_USER(), 'Media', 'UPDATE', NEW.media_id, CONCAT('Updated media: ', NEW.title))"""
    ]
    
    print("Creating triggers...")
    for trigger in triggers:
        try:
            cursor.execute("DROP TRIGGER IF EXISTS " + trigger.split()[2])
            cursor.execute(trigger)
        except Error as e:
            print(f"  Trigger warning: {e}")
    
    conn.commit()
    cursor.close()
    print("Tables, indexes, and triggers created successfully!")

def insert_data(conn):
    """Insert sample data"""
    cursor = conn.cursor()
    db_config = load_secrets()
    cursor.execute(f"USE {db_config['database']}")
    
    print("\nInserting data...")
    
    users = [
        ('admin', 'Admin', 'User', date(1990, 1, 1), 'admin@watchplan.com', 'admin123', 'admin'),
        ('dataguy', 'Data', 'Handler', date(1992, 5, 15), 'dataguy@watchplan.com', 'dataguy123', 'moderator'),
        ('john_doe', 'John', 'Doe', date(1995, 3, 20), 'john.doe@email.com', 'john123', 'user'),
        ('jane_smith', 'Jane', 'Smith', date(1998, 7, 10), 'jane.smith@email.com', 'jane123', 'user'),
        ('alex_brown', 'Alex', 'Brown', date(1993, 11, 5), 'alex.brown@email.com', 'alex123', 'user'),
        ('sarah_wilson', 'Sarah', 'Wilson', date(1996, 9, 25), 'sarah.wilson@email.com', 'sarah123', 'user'),
        ('mike_jones', 'Mike', 'Jones', date(1994, 2, 14), 'mike.jones@email.com', 'mike123', 'user'),
        ('emily_davis', 'Emily', 'Davis', date(1997, 6, 30), 'emily.davis@email.com', 'emily123', 'user'),
        ('david_miller', 'David', 'Miller', date(1991, 12, 8), 'david.miller@email.com', 'david123', 'user'),
        ('lisa_anderson', 'Lisa', 'Anderson', date(1999, 4, 18), 'lisa.anderson@email.com', 'lisa123', 'user'),
        ('chris_taylor', 'Chris', 'Taylor', date(1992, 8, 22), 'chris.taylor@email.com', 'chris123', 'user'),
        ('amanda_white', 'Amanda', 'White', date(1995, 1, 12), 'amanda.white@email.com', 'amanda123', 'user'),
        ('robert_lee', 'Robert', 'Lee', date(1993, 5, 15), 'robert.lee@email.com', 'robert123', 'user'),
        ('jennifer_kim', 'Jennifer', 'Kim', date(1996, 8, 22), 'jennifer.kim@email.com', 'jennifer123', 'user'),
        ('michael_chen', 'Michael', 'Chen', date(1994, 11, 3), 'michael.chen@email.com', 'michael123', 'user'),
        ('sophia_rodriguez', 'Sophia', 'Rodriguez', date(1997, 2, 14), 'sophia.rodriguez@email.com', 'sophia123', 'user'),
        ('william_thomas', 'William', 'Thomas', date(1992, 9, 8), 'william.thomas@email.com', 'william123', 'user'),
        ('olivia_martinez', 'Olivia', 'Martinez', date(1998, 6, 25), 'olivia.martinez@email.com', 'olivia123', 'user'),
        ('james_wilson', 'James', 'Wilson', date(1991, 4, 12), 'james.wilson@email.com', 'james123', 'user'),
        ('isabella_garcia', 'Isabella', 'Garcia', date(1999, 10, 30), 'isabella.garcia@email.com', 'isabella123', 'user'),
        ('benjamin_moore', 'Benjamin', 'Moore', date(1995, 7, 18), 'benjamin.moore@email.com', 'benjamin123', 'user'),
        ('ava_jackson', 'Ava', 'Jackson', date(1996, 12, 5), 'ava.jackson@email.com', 'ava123', 'user'),
        ('daniel_harris', 'Daniel', 'Harris', date(1993, 3, 20), 'daniel.harris@email.com', 'daniel123', 'user'),
        ('mia_clark', 'Mia', 'Clark', date(1997, 8, 15), 'mia.clark@email.com', 'mia123', 'user'),
        ('matthew_lewis', 'Matthew', 'Lewis', date(1994, 1, 28), 'matthew.lewis@email.com', 'matthew123', 'user')
    ]
    
    print("  Inserting users...")
    for user in users:
        cursor.execute("""
            INSERT INTO Users (username, firstname, lastname, DOB, email, password, role)
            VALUES (%s, %s, %s, %s, %s, SHA2(%s, 256), %s)
        """, user)
    print(f"  [OK] Inserted {len(users)} users")
    
    genres = [
        ('G001', 'Action'), ('G002', 'Comedy'), ('G003', 'Drama'), ('G004', 'Thriller'),
        ('G005', 'Romance'), ('G006', 'Sci-Fi'), ('G007', 'Horror'), ('G008', 'Adventure'),
        ('G009', 'Crime'), ('G010', 'Mystery'), ('G011', 'Fantasy'), ('G012', 'Biography'),
        ('G013', 'Family'), ('G014', 'Animation'), ('G015', 'Documentary')
    ]
    
    print("  Inserting genres...")
    cursor.executemany("INSERT INTO genres (genre_id, name) VALUES (%s, %s)", genres)
    print(f"  [OK] Inserted {len(genres)} genres")
    
    media = [
        ('M001', 'The Dark Knight', 'Batman faces the Joker in this epic crime thriller.', 2008, 'Movie', 'PG-13', 'https://example.com/darkknight.jpg', 9.0),
        ('M002', 'Inception', 'A mind-bending sci-fi thriller about dream manipulation.', 2010, 'Movie', 'PG-13', 'https://example.com/inception.jpg', 8.8),
        ('M003', 'Breaking Bad', 'A high school chemistry teacher turned methamphetamine manufacturer.', 2008, 'Series', 'A', 'https://example.com/breakingbad.jpg', 9.5),
        ('M004', 'Game of Thrones', 'Epic fantasy series about noble families fighting for the Iron Throne.', 2011, 'Series', 'A', 'https://example.com/got.jpg', 9.3),
        ('M005', 'The Office', 'A mockumentary about office workers at Dunder Mifflin.', 2005, 'Series', 'PG-13', 'https://example.com/office.jpg', 8.9),
        ('M006', 'Stranger Things', 'Kids in a small town face supernatural forces.', 2016, 'Series', 'U/A 16+', 'https://example.com/stranger.jpg', 8.7),
        ('M007', 'The Shawshank Redemption', 'Two imprisoned men bond over years, finding solace.', 1994, 'Movie', 'A', 'https://example.com/shawshank.jpg', 9.3),
        ('M008', 'Pulp Fiction', 'Interconnected stories of crime in Los Angeles.', 1994, 'Movie', 'A', 'https://example.com/pulpfiction.jpg', 8.9),
        ('M009', 'The Matrix', 'A computer hacker learns about the true nature of reality.', 1999, 'Movie', 'U/A 16+', 'https://example.com/matrix.jpg', 8.7),
        ('M010', 'Interstellar', 'Explorers travel through a wormhole in space.', 2014, 'Movie', 'PG-13', 'https://example.com/interstellar.jpg', 8.6),
        ('M011', 'The Crown', 'Follows the reign of Queen Elizabeth II.', 2016, 'Series', 'U/A 13+', 'https://example.com/crown.jpg', 8.7),
        ('M012', 'House of Cards', 'A ruthless politician manipulates his way to power.', 2013, 'Series', 'A', 'https://example.com/hoc.jpg', 8.7),
        ('M013', 'The Witcher', 'A monster hunter struggles to find his place in a world.', 2019, 'Series', 'U/A 16+', 'https://example.com/witcher.jpg', 8.2),
        ('M014', 'Chernobyl', 'The true story of the 1986 nuclear disaster.', 2019, 'Series', 'A', 'https://example.com/chernobyl.jpg', 9.4),
        ('M015', 'The Mandalorian', 'A lone bounty hunter in the outer reaches of the galaxy.', 2019, 'Series', 'PG-13', 'https://example.com/mandalorian.jpg', 8.7),
        ('M016', 'Parasite', 'A poor family schemes to become employed by a wealthy family.', 2019, 'Movie', 'A', 'https://example.com/parasite.jpg', 8.6),
        ('M017', 'Joker', 'A failed comedian descends into madness and crime.', 2019, 'Movie', 'A', 'https://example.com/joker.jpg', 8.4),
        ('M018', 'Dune', 'A noble family becomes embroiled in a war for a desert planet.', 2021, 'Movie', 'PG-13', 'https://example.com/dune.jpg', 8.0),
        ('M019', 'The Last of Us', 'A post-apocalyptic journey across America.', 2023, 'Series', 'U/A 16+', 'https://example.com/lastofus.jpg', 9.1),
        ('M020', 'Succession', 'A media dynasty family fights for control of the company.', 2018, 'Series', 'A', 'https://example.com/succession.jpg', 8.8),
        ('M021', 'The Godfather', 'The aging patriarch of an organized crime dynasty transfers control.', 1972, 'Movie', 'A', 'https://example.com/godfather.jpg', 9.2),
        ('M022', 'Fight Club', 'An insomniac office worker and a devil-may-care soapmaker form an underground fight club.', 1999, 'Movie', 'A', 'https://example.com/fightclub.jpg', 8.8),
        ('M023', 'Forrest Gump', 'The presidencies of Kennedy and Johnson through the eyes of an Alabama man.', 1994, 'Movie', 'PG-13', 'https://example.com/forrest.jpg', 8.8),
        ('M024', 'The Lord of the Rings: The Fellowship', 'A hobbit embarks on a journey to destroy a powerful ring.', 2001, 'Movie', 'PG-13', 'https://example.com/lotr1.jpg', 8.8),
        ('M025', 'The Avengers', 'Earth\'s mightiest heroes must come together.', 2012, 'Movie', 'PG-13', 'https://example.com/avengers.jpg', 8.0),
        ('M026', 'Titanic', 'A seventeen-year-old aristocrat falls in love with a kind but poor artist.', 1997, 'Movie', 'PG-13', 'https://example.com/titanic.jpg', 7.8),
        ('M027', 'Avatar', 'A paraplegic marine dispatched to the moon Pandora.', 2009, 'Movie', 'PG-13', 'https://example.com/avatar.jpg', 7.8),
        ('M028', 'The Lion King', 'Lion cub and future king Simba searches for his identity.', 1994, 'Movie', 'G', 'https://example.com/lionking.jpg', 8.5),
        ('M029', 'Gladiator', 'A former Roman General sets out to exact vengeance.', 2000, 'Movie', 'U/A 16+', 'https://example.com/gladiator.jpg', 8.5),
        ('M030', 'The Departed', 'An undercover cop and a mole in the police force.', 2006, 'Movie', 'A', 'https://example.com/departed.jpg', 8.5),
        ('M031', 'Squid Game', 'Hundreds of cash-strapped players accept a strange invitation.', 2021, 'Series', 'U/A 16+', 'https://example.com/squidgame.jpg', 8.0),
        ('M032', 'Money Heist', 'A criminal mastermind who goes by "The Professor" plans the biggest heist.', 2017, 'Series', 'U/A 16+', 'https://example.com/moneyheist.jpg', 8.2),
        ('M033', 'Narcos', 'A chronicled look at the criminal exploits of Colombian drug lord Pablo Escobar.', 2015, 'Series', 'A', 'https://example.com/narcos.jpg', 8.8),
        ('M034', 'Peaky Blinders', 'A gangster family epic set in 1919 Birmingham.', 2013, 'Series', 'U/A 16+', 'https://example.com/peaky.jpg', 8.8),
        ('M035', 'Black Mirror', 'An anthology series exploring techno-paranoia.', 2011, 'Series', 'A', 'https://example.com/blackmirror.jpg', 8.8),
        ('M036', 'The Boys', 'A group of vigilantes set out to take down corrupt superheroes.', 2019, 'Series', 'A', 'https://example.com/boys.jpg', 8.7),
        ('M037', 'Better Call Saul', 'The trials and tribulations of criminal lawyer Jimmy McGill.', 2015, 'Series', 'A', 'https://example.com/saul.jpg', 8.8),
        ('M038', 'True Detective', 'Seasonal anthology series in which police investigations unearth personal and professional secrets.', 2014, 'Series', 'A', 'https://example.com/truedetective.jpg', 9.0),
        ('M039', 'Fargo', 'Various chronicles of deception, intrigue and murder in the Midwest.', 2014, 'Series', 'A', 'https://example.com/fargo.jpg', 8.9),
        ('M040', 'Westworld', 'Set at the intersection of the near future and the reimagined past.', 2016, 'Series', 'A', 'https://example.com/westworld.jpg', 8.6)
    ]
    
    print("  Inserting media...")
    cursor.executemany("""
        INSERT INTO Media (media_id, title, description, release_year, media_type, age_rating, poster_image_url, average_rating)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, media)
    print(f"  [OK] Inserted {len(media)} media items")
    
    people = [
        ('P001', 'Christian Bale', date(1974, 1, 30), 'https://example.com/bale.jpg'),
        ('P002', 'Heath Ledger', date(1979, 4, 4), 'https://example.com/ledger.jpg'),
        ('P003', 'Leonardo DiCaprio', date(1974, 11, 11), 'https://example.com/dicaprio.jpg'),
        ('P004', 'Bryan Cranston', date(1956, 3, 7), 'https://example.com/cranston.jpg'),
        ('P005', 'Aaron Paul', date(1979, 8, 27), 'https://example.com/paul.jpg'),
        ('P006', 'Peter Dinklage', date(1969, 6, 11), 'https://example.com/dinklage.jpg'),
        ('P007', 'Steve Carell', date(1962, 8, 16), 'https://example.com/carell.jpg'),
        ('P008', 'Millie Bobby Brown', date(2004, 2, 19), 'https://example.com/brown.jpg'),
        ('P009', 'Morgan Freeman', date(1937, 6, 1), 'https://example.com/freeman.jpg'),
        ('P010', 'John Travolta', date(1954, 2, 18), 'https://example.com/travolta.jpg'),
        ('P011', 'Keanu Reeves', date(1964, 9, 2), 'https://example.com/reeves.jpg'),
        ('P012', 'Matthew McConaughey', date(1969, 11, 4), 'https://example.com/mcconaughey.jpg'),
        ('P013', 'Claire Foy', date(1984, 4, 16), 'https://example.com/foy.jpg'),
        ('P014', 'Kevin Spacey', date(1959, 7, 26), 'https://example.com/spacey.jpg'),
        ('P015', 'Henry Cavill', date(1983, 5, 5), 'https://example.com/cavill.jpg'),
        ('P016', 'Jared Harris', date(1961, 8, 24), 'https://example.com/harris.jpg'),
        ('P017', 'Pedro Pascal', date(1975, 4, 2), 'https://example.com/pascal.jpg'),
        ('P018', 'Song Kang-ho', date(1967, 1, 17), 'https://example.com/kangho.jpg'),
        ('P019', 'Joaquin Phoenix', date(1974, 10, 28), 'https://example.com/phoenix.jpg'),
        ('P020', 'Timothée Chalamet', date(1995, 12, 27), 'https://example.com/chalamet.jpg'),
        ('P021', 'Marlon Brando', date(1924, 4, 3), 'https://example.com/brando.jpg'),
        ('P022', 'Al Pacino', date(1940, 4, 25), 'https://example.com/pacino.jpg'),
        ('P023', 'Brad Pitt', date(1963, 12, 18), 'https://example.com/pitt.jpg'),
        ('P024', 'Tom Hanks', date(1956, 7, 9), 'https://example.com/hanks.jpg'),
        ('P025', 'Elijah Wood', date(1981, 1, 28), 'https://example.com/wood.jpg'),
        ('P026', 'Robert Downey Jr.', date(1965, 4, 4), 'https://example.com/rdj.jpg'),
        ('P027', 'Kate Winslet', date(1975, 10, 5), 'https://example.com/winslet.jpg'),
        ('P028', 'Sam Worthington', date(1976, 8, 2), 'https://example.com/worthington.jpg'),
        ('P029', 'Russell Crowe', date(1964, 4, 7), 'https://example.com/crowe.jpg'),
        ('P030', 'Matt Damon', date(1970, 10, 8), 'https://example.com/damon.jpg'),
        ('P031', 'Lee Jung-jae', date(1972, 12, 15), 'https://example.com/leejung.jpg'),
        ('P032', 'Úrsula Corberó', date(1989, 8, 11), 'https://example.com/corbero.jpg'),
        ('P033', 'Wagner Moura', date(1976, 6, 27), 'https://example.com/moura.jpg'),
        ('P034', 'Cillian Murphy', date(1976, 5, 25), 'https://example.com/murphy.jpg'),
        ('P035', 'Jon Hamm', date(1971, 3, 10), 'https://example.com/hamm.jpg')
    ]
    
    print("  Inserting people...")
    cursor.executemany("INSERT INTO People (person_id, name, birthdate, photo_url) VALUES (%s, %s, %s, %s)", people)
    print(f"  [OK] Inserted {len(people)} people")
    
    media_genres = [
        ('M001', 'G001'), ('M001', 'G003'), ('M001', 'G009'),
        ('M002', 'G001'), ('M002', 'G006'), ('M002', 'G010'),
        ('M003', 'G003'), ('M003', 'G009'),
        ('M004', 'G008'), ('M004', 'G011'), ('M004', 'G003'),
        ('M005', 'G002'), ('M005', 'G003'),
        ('M006', 'G006'), ('M006', 'G010'), ('M006', 'G007'),
        ('M007', 'G003'), ('M007', 'G012'),
        ('M008', 'G001'), ('M008', 'G009'),
        ('M009', 'G001'), ('M009', 'G006'),
        ('M010', 'G006'), ('M010', 'G003'),
        ('M011', 'G003'), ('M011', 'G012'),
        ('M012', 'G003'), ('M012', 'G009'),
        ('M013', 'G008'), ('M013', 'G011'),
        ('M014', 'G003'), ('M014', 'G015'),
        ('M015', 'G006'), ('M015', 'G008'),
        ('M016', 'G003'), ('M016', 'G010'),
        ('M017', 'G003'), ('M017', 'G009'),
        ('M018', 'G006'), ('M018', 'G008'),
        ('M019', 'G006'), ('M019', 'G010'),
        ('M020', 'G003'), ('M020', 'G002')
    ]
    
    print("  Inserting media-genres...")
    cursor.executemany("INSERT INTO Media_Genres (media_id, genre_id) VALUES (%s, %s)", media_genres)
    print(f"  [OK] Inserted {len(media_genres)} media-genre relationships")
    
    media_cast = [
        ('M001', 'P001', 'Bruce Wayne / Batman'), ('M001', 'P002', 'Joker'),
        ('M002', 'P003', 'Dom Cobb'), ('M003', 'P004', 'Walter White'),
        ('M003', 'P005', 'Jesse Pinkman'), ('M004', 'P006', 'Tyrion Lannister'),
        ('M005', 'P007', 'Michael Scott'), ('M006', 'P008', 'Eleven'),
        ('M007', 'P009', 'Ellis Boyd Redding'), ('M008', 'P010', 'Vincent Vega'),
        ('M009', 'P011', 'Neo'), ('M010', 'P012', 'Cooper'),
        ('M011', 'P013', 'Queen Elizabeth II'), ('M012', 'P014', 'Frank Underwood'),
        ('M013', 'P015', 'Geralt of Rivia'), ('M014', 'P016', 'Valery Legasov'),
        ('M015', 'P017', 'Din Djarin'), ('M016', 'P018', 'Kim Ki-taek'),
        ('M017', 'P019', 'Arthur Fleck / Joker'), ('M018', 'P020', 'Paul Atreides'),
        ('M021', 'P021', 'Vito Corleone'), ('M021', 'P022', 'Michael Corleone'),
        ('M022', 'P023', 'Tyler Durden'), ('M023', 'P024', 'Forrest Gump'),
        ('M024', 'P025', 'Frodo Baggins'), ('M025', 'P026', 'Tony Stark / Iron Man'),
        ('M026', 'P027', 'Rose DeWitt Bukater'), ('M027', 'P028', 'Jake Sully'),
        ('M029', 'P029', 'Maximus'), ('M030', 'P030', 'Billy Costigan'),
        ('M031', 'P031', 'Seong Gi-hun'), ('M032', 'P032', 'Tokyo'),
        ('M033', 'P033', 'Pablo Escobar'), ('M034', 'P034', 'Thomas Shelby'),
        ('M035', 'P035', 'Various Characters')
    ]
    
    print("  Inserting media cast...")
    cursor.executemany("INSERT INTO Media_Cast (media_id, person_id, character_name) VALUES (%s, %s, %s)", media_cast)
    print(f"  [OK] Inserted {len(media_cast)} cast members")
    
    episodes = []
    series_episodes = {
        'M003': [('E001', 1, 1, 'Pilot', date(2008, 1, 20)), ('E002', 1, 2, 'Cat\'s in the Bag...', date(2008, 1, 27)),
                 ('E003', 1, 3, '...And the Bag\'s in the River', date(2008, 2, 10)), ('E004', 1, 4, 'Cancer Man', date(2008, 2, 17)),
                 ('E005', 1, 5, 'Gray Matter', date(2008, 2, 24)), ('E006', 1, 6, 'Crazy Handful of Nothin\'', date(2008, 3, 2)),
                 ('E007', 1, 7, 'A No-Rough-Stuff-Type Deal', date(2008, 3, 9)), ('E008', 2, 1, 'Seven Thirty-Seven', date(2009, 3, 8)),
                 ('E009', 2, 2, 'Grilled', date(2009, 3, 15)), ('E010', 2, 3, 'Bit by a Dead Bee', date(2009, 3, 22))],
        'M004': [('E011', 1, 1, 'Winter Is Coming', date(2011, 4, 17)), ('E012', 1, 2, 'The Kingsroad', date(2011, 4, 24)),
                 ('E013', 1, 3, 'Lord Snow', date(2011, 5, 1)), ('E014', 1, 4, 'Cripples, Bastards, and Broken Things', date(2011, 5, 8)),
                 ('E015', 1, 5, 'The Wolf and the Lion', date(2011, 5, 15)), ('E016', 1, 6, 'A Golden Crown', date(2011, 5, 22)),
                 ('E017', 2, 1, 'The North Remembers', date(2012, 4, 1)), ('E018', 2, 2, 'The Night Lands', date(2012, 4, 8))],
        'M005': [('E019', 1, 1, 'Pilot', date(2005, 3, 24)), ('E020', 1, 2, 'Diversity Day', date(2005, 3, 29)),
                 ('E021', 1, 3, 'Health Care', date(2005, 4, 5)), ('E022', 1, 4, 'The Alliance', date(2005, 4, 12)),
                 ('E023', 1, 5, 'Basketball', date(2005, 4, 19)), ('E024', 2, 1, 'The Dundies', date(2005, 9, 20)),
                 ('E025', 2, 2, 'Sexual Harassment', date(2005, 9, 27)), ('E026', 2, 3, 'Office Olympics', date(2005, 10, 4))],
        'M006': [('E027', 1, 1, 'Chapter One: The Vanishing of Will Byers', date(2016, 7, 15)),
                 ('E028', 1, 2, 'Chapter Two: The Weirdo on Maple Street', date(2016, 7, 15)),
                 ('E029', 1, 3, 'Chapter Three: Holly, Jolly', date(2016, 7, 15)),
                 ('E030', 1, 4, 'Chapter Four: The Body', date(2016, 7, 15)),
                 ('E031', 2, 1, 'Chapter One: MADMAX', date(2017, 10, 27)),
                 ('E032', 2, 2, 'Chapter Two: Trick or Treat, Freak', date(2017, 10, 27))],
        'M011': [('E033', 1, 1, 'Wolferton Splash', date(2016, 11, 4)), ('E034', 1, 2, 'Hyde Park Corner', date(2016, 11, 11)),
                 ('E035', 1, 3, 'Windsor', date(2016, 11, 18)), ('E036', 2, 1, 'Misadventure', date(2017, 12, 8))],
        'M012': [('E037', 1, 1, 'Chapter 1', date(2013, 2, 1)), ('E038', 1, 2, 'Chapter 2', date(2013, 2, 8)),
                 ('E039', 1, 3, 'Chapter 3', date(2013, 2, 15)), ('E040', 2, 1, 'Chapter 14', date(2014, 2, 14))],
        'M013': [('E041', 1, 1, 'The End\'s Beginning', date(2019, 12, 20)), ('E042', 1, 2, 'Four Marks', date(2019, 12, 20)),
                 ('E043', 1, 3, 'Betrayer Moon', date(2019, 12, 20)), ('E044', 2, 1, 'A Grain of Truth', date(2021, 12, 17))],
        'M014': [('E045', 1, 1, '1:23:45', date(2019, 5, 6)), ('E046', 1, 2, 'Please Remain Calm', date(2019, 5, 13)),
                 ('E047', 1, 3, 'Open Wide, O Earth', date(2019, 5, 20)), ('E048', 1, 4, 'The Happiness of All Mankind', date(2019, 5, 27))],
        'M015': [('E049', 1, 1, 'Chapter 1', date(2019, 11, 12)), ('E050', 1, 2, 'Chapter 2: The Child', date(2019, 11, 15)),
                 ('E051', 1, 3, 'Chapter 3: The Sin', date(2019, 11, 22)), ('E052', 2, 1, 'Chapter 9', date(2020, 10, 30))],
        'M019': [('E053', 1, 1, 'When You\'re Lost in the Darkness', date(2023, 1, 15)),
                 ('E054', 1, 2, 'Infected', date(2023, 1, 22)),
                 ('E055', 1, 3, 'Long, Long Time', date(2023, 1, 29)),
                 ('E056', 1, 4, 'Please Hold to My Hand', date(2023, 2, 5))],
        'M020': [('E057', 1, 1, 'Celebration', date(2018, 6, 3)), ('E058', 1, 2, 'Shit Show at the Fuck Factory', date(2018, 6, 10)),
                 ('E059', 1, 3, 'Lifeboats', date(2018, 6, 17)), ('E060', 2, 1, 'The Summer Palace', date(2019, 8, 11))],
        'M031': [('E061', 1, 1, 'Red Light, Green Light', date(2021, 9, 17)),
                 ('E062', 1, 2, 'Hell', date(2021, 9, 17)),
                 ('E063', 1, 3, 'The Man with the Umbrella', date(2021, 9, 17))],
        'M032': [('E064', 1, 1, 'Efectuar lo acordado', date(2017, 5, 2)),
                 ('E065', 1, 2, 'Imprudencias letales', date(2017, 5, 9)),
                 ('E066', 1, 3, 'Errar al disparar', date(2017, 5, 16))],
        'M033': [('E067', 1, 1, 'Descenso', date(2015, 8, 28)),
                 ('E068', 1, 2, 'The Sword of Simón Bolívar', date(2015, 9, 4)),
                 ('E069', 1, 3, 'The Men of Always', date(2015, 9, 11))],
        'M034': [('E070', 1, 1, 'Episode 1', date(2013, 9, 12)),
                 ('E071', 1, 2, 'Episode 2', date(2013, 9, 19)),
                 ('E072', 1, 3, 'Episode 3', date(2013, 9, 26))],
        'M035': [('E073', 1, 1, 'The National Anthem', date(2011, 12, 4)),
                 ('E074', 1, 2, 'Fifteen Million Merits', date(2011, 12, 11)),
                 ('E075', 1, 3, 'The Entire History of You', date(2011, 12, 18))],
        'M036': [('E076', 1, 1, 'The Name of the Game', date(2019, 7, 26)),
                 ('E077', 1, 2, 'Cherry', date(2019, 7, 26)),
                 ('E078', 1, 3, 'Get Some', date(2019, 8, 2))],
        'M037': [('E079', 1, 1, 'Uno', date(2015, 2, 8)),
                 ('E080', 1, 2, 'Mijo', date(2015, 2, 9)),
                 ('E081', 1, 3, 'Nacho', date(2015, 2, 16))],
        'M038': [('E082', 1, 1, 'The Long Bright Dark', date(2014, 1, 12)),
                 ('E083', 1, 2, 'Seeing Things', date(2014, 1, 19)),
                 ('E084', 1, 3, 'The Locked Room', date(2014, 1, 26))],
        'M039': [('E085', 1, 1, 'The Crocodile\'s Dilemma', date(2014, 4, 15)),
                 ('E086', 1, 2, 'The Rooster Prince', date(2014, 4, 22)),
                 ('E087', 1, 3, 'A Muddy Road', date(2014, 4, 29))],
        'M040': [('E088', 1, 1, 'The Original', date(2016, 10, 2)),
                 ('E089', 1, 2, 'Chestnut', date(2016, 10, 9)),
                 ('E090', 1, 3, 'The Stray', date(2016, 10, 16))]
    }
    
    for media_id, eps in series_episodes.items():
        for ep in eps:
            episodes.append((ep[0], media_id, ep[1], ep[2], ep[3], ep[4]))
    
    print("  Inserting episodes...")
    cursor.executemany("""
        INSERT INTO Episodes (episode_id, media_id, season_number, episode_number, title, air_date)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, episodes)
    print(f"  [OK] Inserted {len(episodes)} episodes")
    
    playlists = [
        ('PL001', 'john_doe', 'My Favorites'),
        ('PL002', 'john_doe', 'Action Movies'),
        ('PL003', 'jane_smith', 'Must Watch'),
        ('PL004', 'alex_brown', 'Comedy Series'),
        ('PL005', 'sarah_wilson', 'Thriller Collection'),
        ('PL006', 'mike_jones', 'Sci-Fi Classics'),
        ('PL007', 'emily_davis', 'Crime Drama'),
        ('PL008', 'david_miller', 'Fantasy & Adventure'),
        ('PL009', 'lisa_anderson', 'Award Winners'),
        ('PL010', 'chris_taylor', 'Binge Worthy'),
        ('PL011', 'robert_lee', 'Top Rated'),
        ('PL012', 'jennifer_kim', 'Romance & Drama'),
        ('PL013', 'michael_chen', 'Action Packed'),
        ('PL014', 'sophia_rodriguez', 'Mystery Series')
    ]
    
    print("  Inserting playlists...")
    cursor.executemany("INSERT INTO playlist (playlist_id, username, name) VALUES (%s, %s, %s)", playlists)
    print(f"  [OK] Inserted {len(playlists)} playlists")
    
    playlist_items = [
        ('PL001', 'M001'), ('PL001', 'M002'), ('PL001', 'M007'), ('PL001', 'M021'),
        ('PL002', 'M001'), ('PL002', 'M008'), ('PL002', 'M009'), ('PL002', 'M025'),
        ('PL003', 'M003'), ('PL003', 'M004'), ('PL003', 'M014'), ('PL003', 'M038'),
        ('PL004', 'M005'), ('PL004', 'M020'), ('PL004', 'M031'),
        ('PL005', 'M002'), ('PL005', 'M006'), ('PL005', 'M012'), ('PL005', 'M033'),
        ('PL006', 'M002'), ('PL006', 'M009'), ('PL006', 'M010'), ('PL006', 'M015'),
        ('PL007', 'M001'), ('PL007', 'M008'), ('PL007', 'M030'), ('PL007', 'M033'),
        ('PL008', 'M004'), ('PL008', 'M013'), ('PL008', 'M024'), ('PL008', 'M015'),
        ('PL009', 'M007'), ('PL009', 'M016'), ('PL009', 'M021'), ('PL009', 'M023'),
        ('PL010', 'M003'), ('PL010', 'M031'), ('PL010', 'M032'), ('PL010', 'M036'),
        ('PL011', 'M001'), ('PL011', 'M003'), ('PL011', 'M007'), ('PL011', 'M014'),
        ('PL012', 'M023'), ('PL012', 'M026'), ('PL012', 'M011'),
        ('PL013', 'M001'), ('PL013', 'M025'), ('PL013', 'M029'), ('PL013', 'M036'),
        ('PL014', 'M002'), ('PL014', 'M012'), ('PL014', 'M038'), ('PL014', 'M039')
    ]
    
    print("  Inserting playlist items...")
    cursor.executemany("INSERT INTO Playlist_item (playlist_id, media_id) VALUES (%s, %s)", playlist_items)
    print(f"  [OK] Inserted {len(playlist_items)} playlist items")
    
    watchlist_items = [
        ('john_doe', 'M001', 'completed', 9), ('john_doe', 'M002', 'completed', 8),
        ('john_doe', 'M003', 'watching', 10), ('john_doe', 'M007', 'completed', 9),
        ('john_doe', 'M021', 'planned', None), ('jane_smith', 'M004', 'watching', 9),
        ('jane_smith', 'M005', 'completed', 8), ('jane_smith', 'M011', 'watching', 8),
        ('jane_smith', 'M014', 'completed', 10), ('alex_brown', 'M006', 'watching', 8),
        ('alex_brown', 'M005', 'completed', 9), ('alex_brown', 'M020', 'watching', 8),
        ('sarah_wilson', 'M007', 'completed', 10), ('sarah_wilson', 'M002', 'watching', 9),
        ('sarah_wilson', 'M012', 'completed', 8), ('mike_jones', 'M008', 'planned', None),
        ('mike_jones', 'M009', 'completed', 9), ('mike_jones', 'M010', 'watching', 8),
        ('emily_davis', 'M009', 'completed', 9), ('emily_davis', 'M030', 'watching', 8),
        ('emily_davis', 'M033', 'completed', 9), ('david_miller', 'M010', 'watching', 8),
        ('david_miller', 'M015', 'watching', 9), ('david_miller', 'M024', 'planned', None),
        ('lisa_anderson', 'M016', 'completed', 9), ('lisa_anderson', 'M023', 'watching', 8),
        ('chris_taylor', 'M017', 'completed', 8), ('chris_taylor', 'M036', 'watching', 9),
        ('amanda_white', 'M019', 'watching', 9), ('amanda_white', 'M031', 'completed', 8),
        ('robert_lee', 'M022', 'completed', 9), ('jennifer_kim', 'M026', 'watching', 8),
        ('michael_chen', 'M025', 'completed', 8), ('sophia_rodriguez', 'M032', 'watching', 9)
    ]
    
    print("  Inserting watchlist items...")
    for item in watchlist_items:
        if item[3]:
            cursor.execute("""
                INSERT INTO Watchlists_item (username, media_id, status, user_rating)
                VALUES (%s, %s, %s, %s)
            """, item)
        else:
            cursor.execute("""
                INSERT INTO Watchlists_item (username, media_id, status)
                VALUES (%s, %s, %s)
            """, item[:3])
    print(f"  [OK] Inserted {len(watchlist_items)} watchlist items")
    
    series_progress = [
        ('john_doe', 'M003', 'E003'), ('john_doe', 'M006', 'E028'),
        ('jane_smith', 'M004', 'E012'), ('jane_smith', 'M011', 'E033'),
        ('alex_brown', 'M006', 'E028'), ('alex_brown', 'M005', 'E020'),
        ('sarah_wilson', 'M011', 'E033'), ('sarah_wilson', 'M012', 'E037'),
        ('mike_jones', 'M012', 'E037'), ('mike_jones', 'M013', 'E041'),
        ('emily_davis', 'M033', 'E067'), ('david_miller', 'M015', 'E049'),
        ('lisa_anderson', 'M031', 'E061'), ('chris_taylor', 'M036', 'E076'),
        ('amanda_white', 'M019', 'E053'), ('robert_lee', 'M032', 'E064'),
        ('jennifer_kim', 'M034', 'E070'), ('michael_chen', 'M035', 'E073'),
        ('sophia_rodriguez', 'M037', 'E079'), ('william_thomas', 'M038', 'E082')
    ]
    
    print("  Inserting series progress...")
    cursor.executemany("""
        INSERT INTO Series_Progress_Table (username, media_id, last_watched_episode_id)
        VALUES (%s, %s, %s)
    """, series_progress)
    print(f"  [OK] Inserted {len(series_progress)} series progress records")
    
    reviews = [
        ('R001', 'john_doe', 'M001', 'Amazing movie! Best Batman film ever.', 9),
        ('R002', 'jane_smith', 'M004', 'Epic fantasy series with great characters.', 9),
        ('R003', 'alex_brown', 'M006', 'Supernatural thriller that keeps you hooked.', 8),
        ('R004', 'sarah_wilson', 'M007', 'A masterpiece of storytelling.', 10),
        ('R005', 'mike_jones', 'M008', 'Quirky and entertaining crime film.', 8),
        ('R006', 'emily_davis', 'M009', 'Mind-bending sci-fi classic.', 9),
        ('R007', 'david_miller', 'M010', 'Emotional and visually stunning.', 8),
        ('R008', 'lisa_anderson', 'M014', 'Gripping historical drama.', 9),
        ('R009', 'chris_taylor', 'M015', 'Great Star Wars content.', 8),
        ('R010', 'amanda_white', 'M019', 'Outstanding adaptation.', 9),
        ('R011', 'john_doe', 'M002', 'Complex and thought-provoking.', 9),
        ('R012', 'jane_smith', 'M005', 'Hilarious and heartwarming.', 9),
        ('R013', 'alex_brown', 'M020', 'Brilliant writing and acting.', 9),
        ('R014', 'sarah_wilson', 'M003', 'One of the best TV shows ever made.', 10),
        ('R015', 'mike_jones', 'M021', 'A classic that never gets old.', 10),
        ('R016', 'emily_davis', 'M030', 'Intense and well-acted.', 9),
        ('R017', 'david_miller', 'M024', 'Epic fantasy at its finest.', 9),
        ('R018', 'lisa_anderson', 'M016', 'Brilliant social commentary.', 9),
        ('R019', 'chris_taylor', 'M017', 'Dark and powerful performance.', 8),
        ('R020', 'amanda_white', 'M031', 'Addictive and thrilling.', 9),
        ('R021', 'robert_lee', 'M022', 'Mind-blowing twist.', 9),
        ('R022', 'jennifer_kim', 'M026', 'Romantic and tragic.', 8),
        ('R023', 'michael_chen', 'M025', 'Fun superhero action.', 8),
        ('R024', 'sophia_rodriguez', 'M032', 'Clever heist series.', 9),
        ('R025', 'william_thomas', 'M038', 'Atmospheric and mysterious.', 9)
    ]
    
    print("  Inserting reviews...")
    cursor.executemany("""
        INSERT INTO Reviews_Table (review_id, username, media_id, review_text, rating)
        VALUES (%s, %s, %s, %s, %s)
    """, reviews)
    print(f"  [OK] Inserted {len(reviews)} reviews")
    
    friends = [
        ('john_doe', 'jane_smith', 'accepted'), ('john_doe', 'alex_brown', 'accepted'),
        ('john_doe', 'sarah_wilson', 'accepted'), ('jane_smith', 'sarah_wilson', 'accepted'),
        ('jane_smith', 'emily_davis', 'accepted'), ('alex_brown', 'mike_jones', 'pending'),
        ('alex_brown', 'sarah_wilson', 'accepted'), ('sarah_wilson', 'emily_davis', 'accepted'),
        ('sarah_wilson', 'mike_jones', 'accepted'), ('mike_jones', 'david_miller', 'pending'),
        ('mike_jones', 'emily_davis', 'accepted'), ('emily_davis', 'lisa_anderson', 'accepted'),
        ('emily_davis', 'david_miller', 'accepted'), ('david_miller', 'chris_taylor', 'accepted'),
        ('david_miller', 'amanda_white', 'accepted'), ('lisa_anderson', 'chris_taylor', 'accepted'),
        ('lisa_anderson', 'robert_lee', 'pending'), ('chris_taylor', 'amanda_white', 'accepted'),
        ('amanda_white', 'robert_lee', 'accepted'), ('robert_lee', 'jennifer_kim', 'pending'),
        ('jennifer_kim', 'michael_chen', 'accepted'), ('michael_chen', 'sophia_rodriguez', 'accepted'),
        ('sophia_rodriguez', 'william_thomas', 'accepted'), ('william_thomas', 'olivia_martinez', 'pending')
    ]
    
    print("  Inserting friends...")
    cursor.executemany("""
        INSERT INTO Friends (username_1, username_2, status)
        VALUES (%s, %s, %s)
    """, friends)
    print(f"  [OK] Inserted {len(friends)} friend relationships")
    
    media_crew = [
        ('M001', 'P001', 'Actor'), ('M001', 'P002', 'Actor'),
        ('M002', 'P003', 'Actor'), ('M003', 'P004', 'Actor'),
        ('M004', 'P006', 'Actor'), ('M005', 'P007', 'Actor'),
        ('M006', 'P008', 'Actor'), ('M007', 'P009', 'Actor'),
        ('M008', 'P010', 'Actor'), ('M009', 'P011', 'Actor'),
        ('M010', 'P012', 'Actor'), ('M011', 'P013', 'Actor'),
        ('M012', 'P014', 'Actor'), ('M013', 'P015', 'Actor'),
        ('M014', 'P016', 'Actor'), ('M015', 'P017', 'Actor'),
        ('M021', 'P021', 'Actor'), ('M021', 'P022', 'Actor'),
        ('M022', 'P023', 'Actor'), ('M023', 'P024', 'Actor'),
        ('M024', 'P025', 'Actor'), ('M025', 'P026', 'Actor'),
        ('M026', 'P027', 'Actor'), ('M027', 'P028', 'Actor'),
        ('M029', 'P029', 'Actor'), ('M030', 'P030', 'Actor'),
        ('M031', 'P031', 'Actor'), ('M032', 'P032', 'Actor'),
        ('M033', 'P033', 'Actor'), ('M034', 'P034', 'Actor')
    ]
    
    print("  Inserting media crew...")
    cursor.executemany("INSERT INTO Media_Crew (media_id, person_id, role) VALUES (%s, %s, %s)", media_crew)
    print(f"  [OK] Inserted {len(media_crew)} crew members")
    
    conn.commit()
    cursor.close()
    print("\n[SUCCESS] All data inserted successfully!")

def main():
    """Main function to reset and populate database"""
    print("=" * 60)
    print("WatchPlan Database Reset Script")
    print("=" * 60)
    
    if not reset_database():
        print("Failed to reset database. Exiting...")
        return
    
    conn = get_connection(use_database=True)
    if not conn:
        print("Failed to connect to database. Exiting...")
        return
    
    try:
        create_tables(conn)
        insert_data(conn)
        print("\n" + "=" * 60)
        print("Database reset and population completed successfully!")
        print("=" * 60)
    except Error as e:
        print(f"\nError: {e}")
    finally:
        conn.close()
        print("Connection closed.")

if __name__ == "__main__":
    main()

