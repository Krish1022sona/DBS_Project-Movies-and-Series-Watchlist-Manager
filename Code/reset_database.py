import mysql.connector
from mysql.connector import Error
from datetime import date
import random

def load_secrets():
    """Load database credentials"""
    global _cached_db_config
    try:
        if _cached_db_config:
            return _cached_db_config
    except NameError:
        _cached_db_config = None

    import getpass
    password = getpass.getpass("Enter MySQL password: ")
    _cached_db_config = {
        'host': 'localhost',
        'user': 'root',
        'password': password,
        'database': 'Streamsync'
    }
    return _cached_db_config

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
        print("🗑️  Dropping existing database...")
        cursor.execute(f"DROP DATABASE IF EXISTS {db_config['database']}")
        print("🆕 Creating new database...")
        cursor.execute(f"CREATE DATABASE {db_config['database']}")
        cursor.execute(f"USE {db_config['database']}")
        conn.commit()
        print("✅ Database reset successful!")
        return True
    except Error as e:
        print(f"❌ Error resetting database: {e}")
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
    
    print("\n📊 Creating tables...")
    for table in tables:
        try:
            cursor.execute(table)
        except Error as e:
            print(f"  ❌ Error: {e}")
    
    indexes = [
        "CREATE INDEX idx_media_id ON Episodes (media_id)",
        "CREATE INDEX idx_username ON Watchlists_item (username)",
        "CREATE INDEX idx_media_genre ON Media_Genres (media_id, genre_id)",
        "CREATE INDEX idx_user_media ON Series_Progress_Table (username, media_id)",
        "CREATE INDEX idx_genre_id ON Media_Genres (genre_id)",
        "CREATE INDEX idx_media_title ON Media (title)",
        "CREATE INDEX idx_people_name ON People (name)"
    ]
    
    for idx in indexes:
        try:
            cursor.execute(idx)
        except Error as e:
            pass
    
    conn.commit()
    cursor.close()
    print("✅ Tables created!")

def get_comprehensive_data():
    """Return comprehensive Bollywood/Indian entertainment data"""
    
    # Real Bollywood/Indian Movies with accurate data
    movies = [
        # Classics
        ('Sholay', 1975, 'Two criminals are hired by a retired police officer to capture a ruthless dacoit terrorizing a village.', 8.2, 'U/A 13+', ['Action', 'Adventure', 'Drama']),
        ('Mughal-e-Azam', 1960, 'A 16th century love story about a marriage of alliance that gave birth to true love between a Mughal prince and a court dancer.', 8.1, 'U', ['Drama', 'Romance']),
        ('Mother India', 1957, 'In the absence of her husband, a woman struggles to raise her children and keep her family together.', 8.0, 'U', ['Drama', 'Family']),
        ('Dilwale Dulhania Le Jayenge', 1995, 'A young man and woman fall in love on a Europe trip despite being engaged to different people.', 8.1, 'U', ['Romance', 'Comedy', 'Drama']),
        ('Lagaan', 2001, 'The people of a small village in Victorian India stake their future on a game of cricket against their ruthless British rulers.', 8.1, 'U', ['Drama', 'Musical', 'Adventure']),
        
        # 2000s Hits
        ('3 Idiots', 2009, 'Two friends search for their long lost companion who was once their best friend and college roommate.', 8.4, 'U/A 13+', ['Comedy', 'Drama']),
        ('Rang De Basanti', 2006, 'The story of six young Indians who assist an English woman to film a documentary on the freedom fighters from their past.', 8.1, 'U/A 13+', ['Drama', 'Action']),
        ('Taare Zameen Par', 2007, 'An eight-year-old boy is thought to be lazy and a troublemaker until a new art teacher discovers he has dyslexia.', 8.4, 'U', ['Drama', 'Family']),
        ('Kabhi Khushi Kabhie Gham', 2001, 'After marrying a woman his father disapproves of, a man reconnects with his long-lost brother.', 7.4, 'U', ['Drama', 'Romance', 'Family']),
        ('Kal Ho Naa Ho', 2003, 'A terminally ill man falls in love but decides to help her marry his best friend instead.', 7.9, 'U/A 13+', ['Romance', 'Drama']),
        ('Devdas', 2002, 'After his wealthy family prohibits him from marrying the woman he loves, Devdas spirals into alcoholism.', 7.5, 'U/A 13+', ['Drama', 'Romance', 'Musical']),
        ('Swades', 2004, 'A successful Indian scientist returns to rural India to take his nanny to America but is drawn into improving the village.', 8.2, 'U', ['Drama']),
        ('Black', 2005, 'The cathartic tale of a young woman who cant see, hear or talk and the teacher who brings light into her dark world.', 8.1, 'U/A 13+', ['Drama']),
        ('Dil Chahta Hai', 2001, 'Three inseparable childhood friends navigate the complexities of love and relationships.', 8.1, 'U/A 13+', ['Comedy', 'Drama', 'Romance']),
        
        # 2010s Blockbusters
        ('Dangal', 2016, 'Former wrestler Mahavir Singh Phogat trains his daughters to become world-class wrestlers.', 8.3, 'U', ['Biography', 'Drama', 'Action']),
        ('PK', 2014, 'An alien on Earth loses the device he needs to communicate with his spaceship and begins questioning religious dogma.', 8.1, 'U/A 13+', ['Comedy', 'Drama']),
        ('Bajrangi Bhaijaan', 2015, 'An Indian man with a magnanimous heart takes a young mute Pakistani girl back to her homeland to reunite her with her family.', 8.0, 'U', ['Action', 'Adventure', 'Comedy']),
        ('Queen', 2013, 'A Delhi girl travels alone to her honeymoon destination after being jilted by her fiance.', 8.2, 'U/A 13+', ['Comedy', 'Drama']),
        ('Barfi!', 2012, 'Three young people learn that love can neither be defined nor contained by societys norms.', 8.1, 'U', ['Comedy', 'Drama', 'Romance']),
        ('Zindagi Na Milegi Dobara', 2011, 'Three friends take a road trip across Spain and confront their fears.', 8.2, 'U/A 13+', ['Comedy', 'Drama', 'Adventure']),
        ('Kahaani', 2012, 'A pregnant woman searches for her missing husband in Kolkata during the festival of Durga Puja.', 8.1, 'U/A 13+', ['Mystery', 'Thriller']),
        ('Talaash', 2012, 'A policeman investigates a film actors death while dealing with his own grief and marriage problems.', 7.2, 'U/A 13+', ['Crime', 'Drama', 'Mystery']),
        ('Bhaag Milkha Bhaag', 2013, 'The story of athlete Milkha Singhs struggles and triumphs.', 8.2, 'U/A 13+', ['Biography', 'Drama', 'Action']),
        ('Andhadhun', 2018, 'A series of mysterious events change the life of a blind pianist who now must report a crime.', 8.2, 'U/A 13+', ['Crime', 'Thriller', 'Comedy']),
        ('Article 15', 2019, 'A police officer fights against caste discrimination in rural India while investigating a crime.', 8.1, 'U/A 16+', ['Crime', 'Drama', 'Thriller']),
        ('Gully Boy', 2019, 'A street rapper from Mumbai seeks his true calling through music despite opposition from his family.', 7.9, 'U/A 13+', ['Drama', 'Musical']),
        ('Uri: The Surgical Strike', 2019, 'Indian army conducts a covert operation to avenge the killing of fellow army men at their base.', 8.3, 'U/A 13+', ['Action', 'Drama', 'War']),
        ('Tumbbad', 2018, 'A mans greed to obtain a cursed treasure unleashes a dark horror in a small village.', 8.2, 'U/A 16+', ['Drama', 'Fantasy', 'Horror']),
        
        # Recent Blockbusters (2020s)
        ('Baahubali: The Beginning', 2015, 'A young man learns about his royal lineage and destiny to free his kingdom.', 8.0, 'U/A 13+', ['Action', 'Drama', 'Fantasy']),
        ('Baahubali 2: The Conclusion', 2017, 'Amarendra Baahubali faces betrayal while fighting for his kingdom and his love.', 8.2, 'U/A 13+', ['Action', 'Drama', 'Fantasy']),
        ('K.G.F: Chapter 1', 2018, 'An underdog rises from poverty to become a powerful gangster in the gold mines of Kolar.', 8.2, 'U/A 16+', ['Action', 'Crime', 'Drama']),
        ('K.G.F: Chapter 2', 2022, 'Rocky establishes his supremacy over the Kolar Gold Fields while facing new threats.', 8.4, 'U/A 16+', ['Action', 'Crime', 'Drama']),
        ('RRR', 2022, 'A tale of two legendary revolutionaries and their journey away from home before they began fighting for their country.', 7.9, 'U/A 13+', ['Action', 'Drama']),
        ('Pushpa: The Rise', 2021, 'A laborer rises through the ranks of a red sandalwood smuggling syndicate.', 7.6, 'U/A 16+', ['Action', 'Crime', 'Drama']),
        ('Brahmastra: Part One - Shiva', 2022, 'A DJ discovers a mystical power within himself and his connection to an ancient weapon.', 6.3, 'U/A 13+', ['Action', 'Adventure', 'Fantasy']),
        ('Pathaan', 2023, 'An exiled RAW agent is brought back to lead an operation against a mercenary.', 7.0, 'U/A 13+', ['Action', 'Thriller']),
        ('Jawan', 2023, 'A man is driven by a personal vendetta to rectify social injustices.', 7.2, 'U/A 16+', ['Action', 'Thriller']),
        ('Dunki', 2023, 'A group of friends embark on an illegal journey to reach London.', 6.8, 'U/A 13+', ['Comedy', 'Drama']),
        ('Animal', 2023, 'A son embarks on a violent quest for revenge to protect his fathers legacy.', 6.1, 'A', ['Action', 'Crime', 'Drama']),
        ('12th Fail', 2023, 'Based on the true story of IPS officer Manoj Kumar Sharma and his journey from failure to success.', 8.9, 'U/A 13+', ['Biography', 'Drama']),
        ('Rocky Aur Rani Kii Prem Kahaani', 2023, 'Two individuals from different backgrounds fall in love and try to unite their families.', 6.6, 'U/A 13+', ['Comedy', 'Drama', 'Romance']),
        
        # More Popular Films
        ('Drishyam', 2015, 'A man goes to extreme lengths to save his family from consequences after a tragic accident.', 8.2, 'U/A 13+', ['Crime', 'Drama', 'Thriller']),
        ('Drishyam 2', 2022, 'The family faces new challenges as the case reopens after seven years.', 8.2, 'U/A 13+', ['Crime', 'Drama', 'Thriller']),
        ('Stree', 2018, 'In a small town, a mysterious spirit kidnaps men at night during an annual festival.', 7.5, 'U/A 13+', ['Comedy', 'Horror']),
        ('Badhaai Ho', 2018, 'A man faces embarrassment when his middle-aged mother gets pregnant.', 7.9, 'U/A 13+', ['Comedy', 'Drama']),
        ('Dear Zindagi', 2016, 'A budding cinematographer seeks the help of a psychologist to overcome her insecurities.', 7.4, 'U/A 13+', ['Drama', 'Romance']),
        ('Pink', 2016, 'A retired lawyer comes to the defense of three young women in a case of alleged molestation.', 8.1, 'U/A 13+', ['Crime', 'Drama', 'Thriller']),
        ('Piku', 2015, 'A road trip brings a daughter closer to her aging, eccentric father.', 7.6, 'U', ['Comedy', 'Drama']),
        ('Madras Cafe', 2013, 'An Indian intelligence agent journeys to Sri Lanka to investigate a conspiracy during the civil war.', 7.7, 'U/A 16+', ['Action', 'Thriller']),
        ('A Wednesday', 2008, 'A retiring policeman recalls his most memorable case about a mysterious caller who threatens Mumbai.', 8.1, 'U/A 13+', ['Crime', 'Drama', 'Thriller']),
        ('Special 26', 2013, 'A gang poses as CBI officers and executes heists while an actual officer tries to catch them.', 8.0, 'U/A 13+', ['Crime', 'Drama', 'Thriller']),
        ('Raazi', 2018, 'An Indian spy marries a Pakistani military officer during the 1971 war.', 7.7, 'U/A 13+', ['Action', 'Drama', 'Thriller']),
        ('Masaan', 2015, 'Four lives intersect along the Ganges in Varanasi as they deal with love, loss, and redemption.', 8.1, 'U/A 16+', ['Drama']),
        ('Newton', 2017, 'A government clerk struggles to conduct free and fair elections in a conflict-ridden jungle.', 7.7, 'U/A 13+', ['Comedy', 'Drama']),
        ('Haider', 2014, 'A young man returns to Kashmir to find his father and gets drawn into the politics of the state.', 8.1, 'U/A 16+', ['Crime', 'Drama', 'Thriller']),
        ('Omkara', 2006, 'A Bollywood adaptation of Othello set in the heartland of Uttar Pradesh.', 8.0, 'A', ['Crime', 'Drama', 'Thriller']),
        ('Gangs of Wasseypur', 2012, 'A clash between two crime families in the coal mafia of Dhanbad spanning three generations.', 8.2, 'A', ['Action', 'Crime', 'Drama']),
        ('Gangs of Wasseypur 2', 2012, 'Definitive revenge from the coal mafia leads to a bloody war.', 8.2, 'A', ['Action', 'Crime', 'Drama']),
        ('The Lunchbox', 2013, 'A mistaken delivery leads to a correspondence between a young housewife and a lonely widower.', 7.8, 'U', ['Drama', 'Romance']),
        ('Rockstar', 2011, 'A musician seeks to find his true calling through heartbreak and redemption.', 7.7, 'U/A 13+', ['Drama', 'Musical', 'Romance']),
        ('Wake Up Sid', 2009, 'A lazy Mumbai college student transforms after falling in love with an ambitious writer.', 7.6, 'U', ['Comedy', 'Drama', 'Romance']),
        ('Yeh Jawaani Hai Deewani', 2013, 'Four friends reunite for a wedding and rekindle their old bonds and buried feelings.', 7.2, 'U', ['Comedy', 'Drama', 'Romance']),
        ('Tamasha', 2015, 'A man rediscovers his true self when he meets a woman who encourages him to break free.', 7.3, 'U/A 13+', ['Drama', 'Romance']),
        ('Paan Singh Tomar', 2012, 'The true story of an athlete turned dacoit.', 8.2, 'U/A 16+', ['Action', 'Biography', 'Crime']),
        ('Shahid', 2012, 'The story of human rights lawyer and activist Shahid Azmi.', 8.2, 'U/A 13+', ['Biography', 'Crime', 'Drama']),
        ('Aligarh', 2015, 'A professor fights against his suspension for his sexual orientation.', 7.7, 'U/A 16+', ['Biography', 'Drama']),
        ('Udaan', 2010, 'A teenage boy returns home from boarding school and struggles with his oppressive father.', 8.1, 'U/A 13+', ['Drama']),
        ('Ship of Theseus', 2012, 'Three stories explore questions of identity, justice, beauty, and soul.', 8.0, 'U/A 13+', ['Drama']),
        ('Court', 2014, 'A folk singer is accused of inciting a sewage worker to commit suicide through his songs.', 7.7, 'U/A 13+', ['Drama']),
        ('The Dirty Picture', 2011, 'The story of south Indian actress Silk Smitha.', 6.6, 'A', ['Biography', 'Drama']),
        ('Vicky Donor', 2012, 'A man is convinced to be a sperm donor but faces challenges when he falls in love.', 7.8, 'U/A 13+', ['Comedy', 'Romance']),
        ('Dum Laga Ke Haisha', 2015, 'An overweight woman and her husband navigate their arranged marriage.', 7.5, 'U/A 13+', ['Comedy', 'Drama', 'Romance']),
        ('Sui Dhaaga', 2018, 'A man starts his own clothing business to gain respect from his family.', 7.5, 'U', ['Comedy', 'Drama']),
        ('Badla', 2019, 'A dynamic businesswoman is caught in a murder case and hires a reputed lawyer to solve it.', 7.8, 'U/A 13+', ['Crime', 'Drama', 'Mystery']),
        ('Raees', 2017, 'A bootlegger rises to power in Gujarat while an IPS officer is determined to end his reign.', 6.7, 'U/A 16+', ['Action', 'Crime', 'Drama']),
        ('Fan', 2016, 'A fan of a famous film star turns aggressive when his idol refuses to acknowledge him.', 6.9, 'U/A 13+', ['Action', 'Drama', 'Thriller']),
        ('Zero', 2018, 'A vertically challenged man falls in love with a NASA scientist with cerebral palsy.', 5.3, 'U/A 13+', ['Comedy', 'Drama', 'Romance']),
        ('Chak De! India', 2007, 'A disgraced hockey player coaches the Indian womens team to glory.', 8.1, 'U', ['Drama', 'Action']),
        ('Jodhaa Akbar', 2008, 'A sixteenth century love story about a marriage of alliance between Mughal Emperor Akbar and Rajput Princess Jodhaa.', 7.5, 'U', ['Action', 'Drama', 'Romance']),
        ('Guru', 2007, 'A villagers relentless pursuit of success transforms him into a business tycoon.', 7.7, 'U', ['Biography', 'Drama']),
        ('No One Killed Jessica', 2011, 'A journalist and a victims sister fight for justice in a high-profile murder case.', 7.2, 'U/A 16+', ['Biography', 'Crime', 'Drama']),
        ('Airlift', 2016, 'Based on the true story of the largest human evacuation in history during the Kuwait invasion.', 7.9, 'U/A 13+', ['Drama', 'Thriller']),
    ]
    
    # Real Indian Web Series with accurate data
    series = [
        ('Sacred Games', 2018, 'A troubled police officer discovers a plot threatening Mumbai while dealing with his own demons.', 8.6, 'A', ['Crime', 'Drama', 'Thriller'], 2, [8, 8]),
        ('Mirzapur', 2018, 'A clash between gangsters and lawmen in a lawless town in Uttar Pradesh.', 8.4, 'A', ['Action', 'Crime', 'Drama'], 3, [9, 10, 10]),
        ('The Family Man', 2019, 'A middle-class man secretly works for a special cell of the National Investigation Agency.', 8.7, 'U/A 16+', ['Action', 'Drama', 'Thriller'], 2, [10, 9]),
        ('Paatal Lok', 2020, 'A down-and-out cop lands a case that exposes the underbelly of society and his own past.', 7.9, 'A', ['Crime', 'Drama', 'Thriller'], 1, [9]),
        ('Delhi Crime', 2019, 'Based on the 2012 Delhi gang rape case and the subsequent investigation.', 8.5, 'A', ['Crime', 'Drama', 'Thriller'], 2, [7, 5]),
        ('Scam 1992', 2020, 'The rise and fall of stockbroker Harshad Mehta during the 1992 Indian stock market scam.', 9.5, 'U/A 16+', ['Biography', 'Crime', 'Drama'], 1, [10]),
        ('Scam 2003', 2023, 'The story of Abdul Karim Telgi and the stamp paper scam.', 8.2, 'U/A 16+', ['Biography', 'Crime', 'Drama'], 1, [10]),
        ('Kota Factory', 2019, 'Students in Kota preparing for IIT entrance exams face academic and personal challenges.', 8.9, 'U/A 13+', ['Comedy', 'Drama'], 3, [5, 5, 5]),
        ('Panchayat', 2020, 'An engineering graduate reluctantly becomes a village secretary in a remote part of India.', 8.9, 'U/A 13+', ['Comedy', 'Drama'], 3, [8, 8, 8]),
        ('Aspirants', 2021, 'Three UPSC aspirants navigate the challenges of preparing for civil services.', 9.2, 'U/A 13+', ['Drama'], 1, [5]),
        ('TVF Pitchers', 2015, 'Four friends quit their jobs to start their own startup.', 9.1, 'U/A 13+', ['Comedy', 'Drama'], 2, [5, 5]),
        ('Made in Heaven', 2019, 'Wedding planners in Delhi navigate the complexities of Indian marriages.', 8.3, 'A', ['Drama', 'Romance'], 2, [9, 8]),
        ('Breathe', 2018, 'A desperate father goes to extreme lengths to save his dying son.', 7.9, 'U/A 16+', ['Crime', 'Drama', 'Thriller'], 2, [8, 8]),
        ('Little Things', 2016, 'A young couple in Mumbai navigate the ups and downs of their relationship.', 8.0, 'U/A 13+', ['Comedy', 'Drama', 'Romance'], 4, [5, 5, 5, 5]),
        ('Rocket Boys', 2022, 'The story of Homi Bhabha and Vikram Sarabhai building Indias nuclear and space programs.', 8.7, 'U/A 13+', ['Biography', 'Drama'], 2, [4, 4]),
        ('She', 2020, 'A constable goes undercover as a sex worker to catch a crime lord.', 6.5, 'A', ['Crime', 'Drama', 'Thriller'], 2, [7, 8]),
        ('Aarya', 2020, 'A woman joins the crime world to protect her family after her husbands murder.', 7.2, 'U/A 16+', ['Action', 'Crime', 'Drama'], 3, [9, 8, 8]),
        ('Asur', 2020, 'A forensic expert and CBI officer hunt a serial killer who uses mythology.', 8.4, 'A', ['Crime', 'Drama', 'Thriller'], 2, [8, 8]),
        ('Jamtara', 2020, 'A group of young people run a phishing scam from a small town.', 7.2, 'U/A 16+', ['Crime', 'Drama', 'Thriller'], 2, [7, 8]),
        ('Gullak', 2019, 'A middle-class family deals with everyday life in small-town India.', 8.8, 'U', ['Comedy', 'Drama', 'Family'], 3, [5, 5, 5]),
        ('Permanent Roommates', 2014, 'A long-distance couple decides to get married but faces challenges.', 8.4, 'U/A 13+', ['Comedy', 'Romance'], 3, [5, 7, 5]),
        ('Yeh Meri Family', 2018, 'A nostalgic look at a middle-class family in the summer of 1998.', 9.1, 'U', ['Comedy', 'Drama', 'Family'], 2, [6, 6]),
        ('Tripling', 2016, 'Three estranged siblings take a road trip to find themselves.', 8.4, 'U/A 13+', ['Comedy', 'Drama'], 3, [5, 5, 5]),
        ('Bard of Blood', 2019, 'A former RAW agent is pulled back for a covert mission in Balochistan.', 6.8, 'A', ['Action', 'Crime', 'Thriller'], 1, [7]),
        ('Special Ops', 2020, 'A RAW agent hunts for the mastermind behind several terror attacks.', 8.0, 'U/A 16+', ['Action', 'Drama', 'Thriller'], 2, [8, 8]),
        ('Mumbai Diaries 26/11', 2021, 'Doctors and nurses face chaos during the 2008 Mumbai terror attacks.', 8.4, 'U/A 16+', ['Drama', 'Thriller'], 2, [8, 7]),
        ('Selection Day', 2018, 'Two brothers from a village pursue their dream of becoming cricket stars.', 7.5, 'U/A 13+', ['Drama'], 2, [6, 6]),
        ('Taj Mahal 1989', 2020, 'Love stories unfold in a quaint town during 1989.', 6.3, 'U/A 13+', ['Drama', 'Romance'], 1, [7]),
        ('College Romance', 2018, 'Three best friends navigate college life, friendships, and love.', 8.8, 'U/A 13+', ['Comedy', 'Drama', 'Romance'], 3, [5, 5, 5]),
        ('ImMature', 2019, 'A teenager struggles through the awkwardness of adolescence.', 8.5, 'U/A 13+', ['Comedy', 'Drama'], 3, [5, 5, 5]),
        ('Flames', 2018, 'A teenage couple navigates their first relationship.', 8.2, 'U/A 13+', ['Comedy', 'Drama', 'Romance'], 4, [5, 5, 5, 5]),
        ('Girls Hostel', 2018, 'Girls in a hostel deal with friendship, love, and growing up.', 7.9, 'U/A 13+', ['Comedy', 'Drama'], 3, [5, 5, 5]),
    ]
    
    # Real Bollywood/Indian Actors, Directors, and Crew
    people = [
        # Legendary Actors
        ('Amitabh Bachchan', date(1942, 10, 11)),
        ('Shah Rukh Khan', date(1965, 11, 2)),
        ('Aamir Khan', date(1965, 3, 14)),
        ('Salman Khan', date(1965, 12, 27)),
        ('Akshay Kumar', date(1967, 9, 9)),
        ('Hrithik Roshan', date(1974, 1, 10)),
        ('Ajay Devgn', date(1969, 4, 2)),
        ('Ranbir Kapoor', date(1982, 9, 28)),
        ('Ranveer Singh', date(1985, 7, 6)),
        ('Vicky Kaushal', date(1988, 5, 16)),
        ('Rajkummar Rao', date(1984, 8, 31)),
        ('Ayushmann Khurrana', date(1984, 9, 14)),
        ('Varun Dhawan', date(1987, 4, 24)),
        ('Sidharth Malhotra', date(1985, 1, 16)),
        ('Irrfan Khan', date(1967, 1, 7)),
        ('Nawazuddin Siddiqui', date(1974, 5, 19)),
        ('Manoj Bajpayee', date(1969, 4, 23)),
        ('Pankaj Tripathi', date(1976, 9, 5)),
        ('Kay Kay Menon', date(1966, 10, 2)),
        ('Naseeruddin Shah', date(1950, 7, 20)),
        ('Anupam Kher', date(1955, 3, 7)),
        ('Boman Irani', date(1959, 12, 2)),
        ('Paresh Rawal', date(1955, 5, 30)),
        ('Sanjay Dutt', date(1959, 7, 29)),
        ('Anil Kapoor', date(1956, 12, 24)),
        ('Jackie Shroff', date(1957, 2, 1)),
        ('Dharmendra', date(1935, 12, 8)),
        ('Vinod Khanna', date(1946, 10, 6)),
        ('Dilip Kumar', date(1922, 12, 11)),
        ('Dev Anand', date(1923, 9, 26)),
        ('Raj Kapoor', date(1924, 12, 14)),
        ('Sanjeev Kumar', date(1938, 7, 9)),
        ('Jeetendra', date(1942, 4, 7)),
        ('Rajesh Khanna', date(1942, 12, 29)),
        
        # South Indian Stars
        ('Prabhas', date(1979, 10, 23)),
        ('Yash', date(1986, 1, 8)),
        ('Allu Arjun', date(1982, 4, 8)),
        ('Ram Charan', date(1985, 3, 27)),
        ('Jr NTR', date(1983, 5, 20)),
        ('Mahesh Babu', date(1975, 8, 9)),
        ('Vijay', date(1974, 6, 22)),
        ('Ajith Kumar', date(1971, 5, 1)),
        ('Suriya', date(1975, 7, 23)),
        ('Dhanush', date(1983, 7, 28)),
        ('Rajinikanth', date(1950, 12, 12)),
        ('Kamal Haasan', date(1954, 11, 7)),
        ('Chiranjeevi', date(1955, 8, 22)),
        ('Venkatesh', date(1960, 12, 13)),
        
        # Legendary Actresses
        ('Madhuri Dixit', date(1967, 5, 15)),
        ('Sridevi', date(1963, 8, 13)),
        ('Kajol', date(1974, 8, 5)),
        ('Rani Mukerji', date(1978, 3, 21)),
        ('Preity Zinta', date(1975, 1, 31)),
        ('Aishwarya Rai', date(1973, 11, 1)),
        ('Kareena Kapoor Khan', date(1980, 9, 21)),
        ('Priyanka Chopra', date(1982, 7, 18)),
        ('Deepika Padukone', date(1986, 1, 5)),
        ('Katrina Kaif', date(1983, 7, 16)),
        ('Anushka Sharma', date(1988, 5, 1)),
        ('Alia Bhatt', date(1993, 3, 15)),
        ('Kangana Ranaut', date(1987, 3, 23)),
        ('Vidya Balan', date(1979, 1, 1)),
        ('Tabu', date(1971, 11, 4)),
        ('Konkona Sen Sharma', date(1979, 12, 3)),
        ('Radhika Apte', date(1985, 9, 7)),
        ('Kiara Advani', date(1991, 7, 31)),
        ('Shraddha Kapoor', date(1987, 3, 3)),
        ('Kriti Sanon', date(1990, 7, 27)),
        ('Sara Ali Khan', date(1995, 8, 12)),
        ('Janhvi Kapoor', date(1997, 3, 6)),
        ('Ananya Panday', date(1998, 10, 30)),
        ('Sonam Kapoor', date(1985, 6, 9)),
        ('Parineeti Chopra', date(1988, 10, 22)),
        ('Sonakshi Sinha', date(1987, 6, 2)),
        ('Jacqueline Fernandez', date(1985, 8, 11)),
        ('Nargis Fakhri', date(1979, 10, 20)),
        ('Hema Malini', date(1948, 10, 16)),
        ('Rekha', date(1954, 10, 10)),
        ('Jaya Bachchan', date(1948, 4, 9)),
        ('Shabana Azmi', date(1950, 9, 18)),
        ('Smita Patil', date(1955, 10, 17)),
        ('Waheeda Rehman', date(1938, 2, 3)),
        ('Nutan', date(1936, 6, 4)),
        ('Meena Kumari', date(1933, 8, 1)),
        
        # Directors
        ('Rajkumar Hirani', date(1962, 11, 20)),
        ('Sanjay Leela Bhansali', date(1963, 2, 24)),
        ('Karan Johar', date(1972, 5, 25)),
        ('Zoya Akhtar', date(1972, 10, 14)),
        ('Anurag Kashyap', date(1972, 9, 10)),
        ('Vishal Bhardwaj', date(1965, 8, 4)),
        ('Imtiaz Ali', date(1971, 6, 16)),
        ('Farhan Akhtar', date(1974, 1, 9)),
        ('Ashutosh Gowariker', date(1964, 2, 15)),
        ('Rakeysh Omprakash Mehra', date(1963, 7, 7)),
        ('Rohit Shetty', date(1973, 3, 14)),
        ('S. S. Rajamouli', date(1973, 10, 10)),
        ('Prashanth Neel', date(1980, 6, 4)),
        ('Atlee', date(1986, 9, 21)),
        ('Sukumar', date(1970, 1, 11)),
        ('Sandeep Reddy Vanga', date(1981, 12, 25)),
        ('Kabir Khan', date(1971, 4, 14)),
        ('Shoojit Sircar', date(1967, 5, 8)),
        ('Neeraj Pandey', date(1973, 12, 17)),
        ('Meghna Gulzar', date(1973, 12, 13)),
        ('Hansal Mehta', date(1968, 12, 29)),
        ('Vikramaditya Motwane', date(1976, 6, 6)),
        ('Dibakar Banerjee', date(1969, 6, 21)),
        ('Anurag Basu', date(1974, 5, 8)),
        ('Nitesh Tiwari', date(1973, 5, 8)),
        ('Amit Sharma', date(1982, 7, 15)),
        ('Richie Mehta', date(1974, 10, 31)),
        ('Varun Grover', date(1980, 1, 26)),
        
        # Writers & Producers
        ('Javed Akhtar', date(1945, 1, 17)),
        ('Salim Khan', date(1935, 11, 24)),
        ('Gulzar', date(1934, 8, 18)),
        ('Juhi Chaturvedi', date(1974, 3, 14)),
        ('Anvita Dutt', date(1974, 8, 7)),
        ('Vidhu Vinod Chopra', date(1952, 9, 5)),
        ('Aditya Chopra', date(1971, 5, 21)),
        ('Yash Chopra', date(1932, 9, 27)),
        ('Sajid Nadiadwala', date(1966, 2, 18)),
        ('Dinesh Vijan', date(1983, 7, 26)),
        ('Ramesh Taurani', date(1959, 1, 21)),
        ('Bhushan Kumar', date(1977, 11, 27)),
        ('Ekta Kapoor', date(1975, 6, 7)),
        ('Aanand L Rai', date(1971, 6, 28)),
        
        # Music Directors
        ('A. R. Rahman', date(1967, 1, 6)),
        ('Amit Trivedi', date(1979, 4, 8)),
        ('Pritam', date(1971, 6, 14)),
        ('Vishal-Shekhar', date(1973, 11, 11)),
        ('Shankar-Ehsaan-Loy', date(1963, 3, 26)),
        ('Anu Malik', date(1960, 11, 2)),
        ('Jatin-Lalit', date(1958, 10, 31)),
    ]
    
    return movies, series, people

def insert_comprehensive_data(conn):
    """Insert comprehensive Bollywood/Indian data"""
    cursor = conn.cursor()
    
    print("\n🎬 Inserting comprehensive Bollywood/Indian data...")
    
    # --- Users ---
    print("\n👥 Creating users...")
    users = [
        ('admin', 'Admin', 'User', date(1990, 1, 1), 'admin@streamsync.com', 'admin123', 'admin'),
        ('moderator', 'Mod', 'User', date(1992, 5, 15), 'mod@streamsync.com', 'mod123', 'moderator')
    ]
    
    for i in range(1, 151):
        users.append((
            f'user{i:03d}', f'User{i:03d}', 'Demo',
            date(1985 + (i % 20), (i % 12) + 1, ((i * 3) % 28) + 1),
            f'user{i:03d}@example.com', f'password{i:03d}', 'user'
        ))
    
    cursor.executemany("""
        INSERT INTO Users (username, firstname, lastname, DOB, email, password, role)
        VALUES (%s, %s, %s, %s, %s, SHA2(%s, 256), %s)
    """, users)
    print(f"  ✅ {len(users)} users created")
    
    # --- Genres ---
    print("\n🎭 Creating genres...")
    genres = [
        ('G001', 'Action'), ('G002', 'Comedy'), ('G003', 'Drama'), ('G004', 'Thriller'),
        ('G005', 'Romance'), ('G006', 'Musical'), ('G007', 'Crime'), ('G008', 'Fantasy'),
        ('G009', 'Biography'), ('G010', 'Family'), ('G011', 'Documentary'), ('G012', 'Adventure'),
        ('G013', 'Horror'), ('G014', 'Mystery'), ('G015', 'War'), ('G016', 'Sci-Fi')
    ]
    cursor.executemany("INSERT INTO genres (genre_id, name) VALUES (%s, %s)", genres)
    print(f"  ✅ {len(genres)} genres created")
    
    # Get data
    movies_data, series_data, people_data = get_comprehensive_data()
    
    # Create genre name to ID mapping
    genre_map = {g[1]: g[0] for g in genres}
    
    # --- Insert Movies ---
    print(f"\n🎥 Inserting {len(movies_data)} movies...")
    media = []
    media_genres = []
    
    for idx, (title, year, desc, rating, age_rating, movie_genres) in enumerate(movies_data, 1):
        media_id = f'M{idx:04d}'
        media.append((media_id, title, desc, year, 'Movie', age_rating, None, rating))
        
        # Add genres
        for genre_name in movie_genres:
            if genre_name in genre_map:
                media_genres.append((media_id, genre_map[genre_name]))
    
    cursor.executemany("""
        INSERT INTO Media (media_id, title, description, release_year, media_type, age_rating, poster_image_url, average_rating)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, media)
    print(f"  ✅ {len(media)} movies inserted")
    
    # --- Insert Series ---
    print(f"\n📺 Inserting {len(series_data)} series...")
    series_media = []
    episodes = []
    episode_counter = 1
    series_start_idx = len(media) + 1
    
    for idx, (title, year, desc, rating, age_rating, show_genres, num_seasons, episodes_per_season) in enumerate(series_data, series_start_idx):
        media_id = f'M{idx:04d}'
        series_media.append((media_id, title, desc, year, 'Series', age_rating, None, rating))
        
        # Add genres
        for genre_name in show_genres:
            if genre_name in genre_map:
                media_genres.append((media_id, genre_map[genre_name]))
        
        # Create episodes
        for season in range(1, num_seasons + 1):
            for ep in range(1, episodes_per_season[season - 1] + 1):
                episode_id = f'E{episode_counter:05d}'
                ep_title = f'{title} S{season}E{ep}'
                air_date = date(year + season - 1, (ep % 12) + 1, min((ep * 3) % 28 + 1, 28))
                episodes.append((episode_id, media_id, season, ep, ep_title, air_date))
                episode_counter += 1
    
    cursor.executemany("""
        INSERT INTO Media (media_id, title, description, release_year, media_type, age_rating, poster_image_url, average_rating)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, series_media)
    print(f"  ✅ {len(series_media)} series inserted")
    
    media.extend(series_media)
    
    # --- Insert Episodes ---
    if episodes:
        print(f"\n📺 Inserting {len(episodes)} episodes...")
        cursor.executemany("""
            INSERT INTO Episodes (episode_id, media_id, season_number, episode_number, title, air_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, episodes)
        print(f"  ✅ {len(episodes)} episodes inserted")
    
    # --- Insert People ---
    print(f"\n👥 Inserting {len(people_data)} people...")
    people = []
    for idx, (name, birthdate) in enumerate(people_data, 1):
        person_id = f'P{idx:04d}'
        people.append((person_id, name, birthdate, None))
    
    cursor.executemany("INSERT INTO People (person_id, name, birthdate, photo_url) VALUES (%s, %s, %s, %s)", people)
    print(f"  ✅ {len(people)} people inserted")
    
    # --- Insert Media-Genre relationships ---
    print(f"\n🎭 Inserting media-genre relationships...")
    media_genres = list(set(media_genres))  # Deduplicate
    cursor.executemany("INSERT INTO Media_Genres (media_id, genre_id) VALUES (%s, %s)", media_genres)
    print(f"  ✅ {len(media_genres)} relationships created")
    
    # --- Assign Cast and Crew to Media ---
    print(f"\n🎬 Assigning cast and crew to media...")
    
    # Create mappings for realistic assignments
    media_ids = [m[0] for m in media]
    person_ids = [p[0] for p in people]
    
    # Assign 3-8 cast members per media
    media_cast = []
    for mid in media_ids:
        num_cast = random.randint(3, 8)
        cast_members = random.sample(person_ids, min(num_cast, len(person_ids)))
        for pid in cast_members:
            character = random.choice(['Lead Role', 'Supporting Role', 'Special Appearance', 'Cameo', 'Antagonist', 'Protagonist'])
            media_cast.append((mid, pid, character))
    
    media_cast = list({(m, p): (m, p, c) for m, p, c in media_cast}.values())
    cursor.executemany("INSERT INTO Media_Cast (media_id, person_id, character_name) VALUES (%s, %s, %s)", media_cast)
    print(f"  ✅ {len(media_cast)} cast assignments")
    
    # Assign 1-3 crew members per media (directors, writers, producers)
    media_crew = []
    for mid in media_ids:
        num_crew = random.randint(1, 3)
        crew_members = random.sample(person_ids, min(num_crew, len(person_ids)))
        for idx, pid in enumerate(crew_members):
            role = ['Director', 'Writer', 'Producer', 'Music Director'][idx % 4]
            media_crew.append((mid, pid, role))
    
    media_crew = list({(m, p, r): (m, p, r) for m, p, r in media_crew}.values())
    cursor.executemany("INSERT INTO Media_Crew (media_id, person_id, role) VALUES (%s, %s, %s)", media_crew)
    print(f"  ✅ {len(media_crew)} crew assignments")
    
    # --- User Activity Data ---
    print("\n👤 Creating user activity data...")
    
    users_list = [u[0] for u in users]
    series_ids = [m[0] for m in media if m[4] == 'Series']
    
    # Playlists
    print("  📋 Creating playlists...")
    playlists = []
    playlist_items = []
    plid = 1
    for user in random.sample(users_list, k=min(100, len(users_list))):
        num_pl = random.randint(1, 4)
        for _ in range(num_pl):
            pid = f'PL{plid:05d}'
            name = random.choice(['Favorites', 'Watch Later', 'Top Bollywood', 'Family Movies', 'Thriller Collection', 'Weekend Binge'])
            playlists.append((pid, user, name))
            items = random.sample(media_ids, k=min(random.randint(5, 20), len(media_ids)))
            for m in items:
                playlist_items.append((pid, m))
            plid += 1
    
    cursor.executemany("INSERT INTO playlist (playlist_id, username, name) VALUES (%s, %s, %s)", playlists)
    cursor.executemany("INSERT INTO Playlist_item (playlist_id, media_id) VALUES (%s, %s)", playlist_items)
    print(f"    ✅ {len(playlists)} playlists with {len(playlist_items)} items")
    
    # Reviews
    print("  ⭐ Creating reviews...")
    reviews = []
    rid = 1
    review_texts = [
        'Masterpiece! One of the best films ever made.',
        'Brilliant performances by the entire cast.',
        'Engaging storyline with great direction.',
        'A must-watch for all cinema lovers.',
        'Good movie but could have been better.',
        'Average film with some good moments.',
        'Disappointing compared to expectations.',
        'Waste of time. Would not recommend.',
        'Fantastic direction and cinematography!',
        'Loved every moment of it. Highly recommended!',
        'The music and visuals are stunning.',
        'A rollercoaster of emotions. Superb!',
        'Not my cup of tea but well executed.',
        'Outstanding performances all around.',
        'An emotional journey worth experiencing.'
    ]
    
    for user in random.sample(users_list, k=min(200, len(users_list))):
        for m in random.sample(media_ids, k=random.randint(2, 12)):
            review_id = f'R{rid:06d}'
            text = random.choice(review_texts)
            rating = random.randint(4, 10)
            reviews.append((review_id, user, m, text, rating))
            rid += 1
    
    cursor.executemany("INSERT INTO Reviews_Table (review_id, username, media_id, review_text, rating) VALUES (%s, %s, %s, %s, %s)", reviews)
    print(f"    ✅ {len(reviews)} reviews")
    
    # Series Progress
    if series_ids and episodes:
        print("  📺 Creating series progress...")
        series_progress = []
        episode_ids = [e[0] for e in episodes]
        for user in random.sample(users_list, k=min(120, len(users_list))):
            for s in random.sample(series_ids, k=min(random.randint(1, 6), len(series_ids))):
                series_episodes = [e[0] for e in episodes if e[1] == s]
                if series_episodes:
                    last_ep = random.choice(series_episodes)
                    series_progress.append((user, s, last_ep))
        
        if series_progress:
            cursor.executemany("INSERT INTO Series_Progress_Table (username, media_id, last_watched_episode_id) VALUES (%s, %s, %s)", series_progress)
            print(f"    ✅ {len(series_progress)} progress records")
    
    # Friends
    print("  👥 Creating friend relationships...")
    friends = []
    for user in random.sample(users_list, k=min(140, len(users_list))):
        others = [u for u in users_list if u != user]
        for friend in random.sample(others, k=min(random.randint(3, 15), len(others))):
            status = random.choice(['accepted', 'accepted', 'accepted', 'pending'])
            friends.append((user, friend, status))
    
    friends = list({(a, b): (a, b, s) for a, b, s in friends}.values())
    cursor.executemany("INSERT INTO Friends (username_1, username_2, status) VALUES (%s, %s, %s)", friends)
    print(f"    ✅ {len(friends)} friendships")
    
    # Watchlist items
    print("  📝 Creating watchlist items...")
    watchlist_items = []
    statuses = ['watching', 'completed', 'planned', 'dropped']
    for user in random.sample(users_list, k=min(130, len(users_list))):
        for m in random.sample(media_ids, k=random.randint(3, 15)):
            status = random.choice(statuses)
            rating = random.randint(6, 10) if status == 'completed' and random.random() > 0.3 else None
            watchlist_items.append((user, m, status, rating))
    
    for item in watchlist_items:
        if item[3] is not None:
            cursor.execute("INSERT INTO Watchlists_item (username, media_id, status, user_rating) VALUES (%s, %s, %s, %s)", item)
        else:
            cursor.execute("INSERT INTO Watchlists_item (username, media_id, status) VALUES (%s, %s, %s)", (item[0], item[1], item[2]))
    
    print(f"    ✅ {len(watchlist_items)} watchlist items")
    
    conn.commit()
    cursor.close()
    print("\n✅ All data inserted successfully!")

def display_statistics(conn):
    """Display database statistics"""
    cursor = conn.cursor()
    
    print("\n" + "="*60)
    print("📊 DATABASE STATISTICS")
    print("="*60)
    
    tables = [
        ('Users', 'Total Users'),
        ('Media', 'Total Media Items'),
        ('Episodes', 'Total Episodes'),
        ('People', 'Total People (Cast & Crew)'),
        ('genres', 'Total Genres'),
        ('Reviews_Table', 'Total Reviews'),
        ('playlist', 'Total Playlists'),
        ('Watchlists_item', 'Total Watchlist Items'),
        ('Friends', 'Total Friendships'),
        ('Media_Cast', 'Total Cast Assignments'),
        ('Media_Crew', 'Total Crew Assignments'),
        ('Media_Genres', 'Total Media-Genre Links'),
        ('Series_Progress_Table', 'Series Progress Records')
    ]
    
    for table, description in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {description:.<40} {count:>6}")
    
    # Additional statistics
    cursor.execute("SELECT COUNT(*) FROM Media WHERE media_type = 'Movie'")
    movies = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM Media WHERE media_type = 'Series'")
    series = cursor.fetchone()[0]
    
    print("\n" + "-"*60)
    print(f"  Movies:................................ {movies:>6}")
    print(f"  Series:................................ {series:>6}")
    
    cursor.execute("SELECT AVG(average_rating) FROM Media WHERE average_rating IS NOT NULL")
    avg_rating = cursor.fetchone()[0]
    if avg_rating:
        print(f"  Average Media Rating:.................. {avg_rating:>6.2f}")
    
    cursor.execute("SELECT COUNT(DISTINCT username) FROM Reviews_Table")
    active_reviewers = cursor.fetchone()[0]
    print(f"  Active Reviewers:...................... {active_reviewers:>6}")
    
    print("="*60)
    
    cursor.close()

def main():
    """Main execution function"""
    print("\n" + "="*60)
    print("  🎬 STREAMSYNC DATABASE SETUP UTILITY 🎬")
    print("="*60)
    
    # Reset database
    conn = get_connection()
    if not conn:
        print("❌ Failed to connect to MySQL server!")
        return
    
    if not reset_database():
        print("❌ Failed to reset database!")
        conn.close()
        return
    
    conn.close()
    
    # Reconnect with database selected
    conn = get_connection(use_database=True)
    if not conn:
        print("❌ Failed to reconnect to database!")
        return
    
    try:
        # Create tables
        create_tables(conn)
        
        # Insert data
        insert_comprehensive_data(conn)
        
        # Display statistics
        display_statistics(conn)
        
        print("\n✅ Database setup completed successfully!")
        print("\n💡 You can now use the database with:")
        print("   - Username: admin, Password: admin123 (Admin)")
        print("   - Username: moderator, Password: mod123 (Moderator)")
        print("   - Username: user001-user150, Password: password001-password150 (Users)")
        
    except Error as e:
        print(f"\n❌ Error during setup: {e}")
        conn.rollback()
    finally:
        conn.close()
        print("\n🔌 Database connection closed.")

if __name__ == "__main__":
    main()