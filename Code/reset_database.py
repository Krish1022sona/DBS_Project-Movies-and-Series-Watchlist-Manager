import mysql.connector
from mysql.connector import Error
import toml
import os
from datetime import datetime, date
import requests
import time
import random
from urllib.parse import quote_plus

def load_secrets():
    """Load database credentials - prompt for password. Cache result so we only ask once."""
    # Cache the DB config so repeated calls don't re-prompt for password
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


def _get_tmdb_api_key():
    """Return TMDB API key from environment variable TMDB_API_KEY or None."""
    return os.environ.get('TMDB_API_KEY')


def _tmdb_search_poster(title, media_type='movie'):
    """Search TMDB for a title (movie or tv) and return an absolute poster URL or None.
    This requires TMDB_API_KEY set in the environment. If not present, returns None.
    """
    api_key = _get_tmdb_api_key()
    if not api_key:
        return None
    try:
        if media_type == 'movie':
            url = f"https://api.themoviedb.org/3/search/movie?api_key={api_key}&query={quote_plus(title)}&region=IN"
        else:
            url = f"https://api.themoviedb.org/3/search/tv?api_key={api_key}&query={quote_plus(title)}&region=IN"
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        results = resp.json().get('results', [])
        if not results:
            return None
        poster_path = results[0].get('poster_path')
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}"
    except Exception as e:
        print(f"TMDB poster fetch error for '{title}': {e}")
    return None


def _tmdb_search_person_photo(name):
    """Search TMDB for a person and return an absolute profile URL or None."""
    api_key = _get_tmdb_api_key()
    if not api_key:
        return None
    try:
        url = f"https://api.themoviedb.org/3/search/person?api_key={api_key}&query={quote_plus(name)}&region=IN"
        resp = requests.get(url, timeout=8)
        resp.raise_for_status()
        results = resp.json().get('results', [])
        if not results:
            return None
        profile_path = results[0].get('profile_path')
        if profile_path:
            return f"https://image.tmdb.org/t/p/w300{profile_path}"
    except Exception as e:
        print(f"TMDB person fetch error for '{name}': {e}")
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
    """Insert sample data (fully Indianized seeds). This replaces ALL seeded rows so IDs and FKs are consistent."""
    cursor = conn.cursor()
    db_config = load_secrets()
    cursor.execute(f"USE {db_config['database']}")

    print("\nInserting data (full Indian seeds, expanded)...")

    # --- Users ---
    # Keep a few admin/demo users then programmatically generate many more
    users = [
        ('admin', 'Admin', 'User', date(1990, 1, 1), 'admin@watchplan.com', 'admin123', 'admin'),
        ('dataguy', 'Data', 'Handler', date(1992, 5, 15), 'dataguy@watchplan.com', 'dataguy123', 'moderator')
    ]

    # generate 150 additional demo users
    for i in range(1, 151):
        uname = f'user{i:03d}'
        fname = f'User{i:03d}'
        lname = 'Test'
        dob = date(1985 + (i % 20), (i % 12) + 1, ((i * 3) % 28) + 1)
        email = f'user{i:03d}@example.com'
        password = f'password{i:03d}'
        role = 'user'
        users.append((uname, fname, lname, dob, email, password, role))

    cursor.executemany("""
        INSERT INTO Users (username, firstname, lastname, DOB, email, password, role)
        VALUES (%s, %s, %s, %s, %s, SHA2(%s, 256), %s)
    """, users)
    print(f"  [OK] Inserted {len(users)} users")

    # --- Genres ---
    genres = [
        ('G001', 'Action'), ('G002', 'Comedy'), ('G003', 'Drama'), ('G004', 'Thriller'),
        ('G005', 'Romance'), ('G006', 'Musical'), ('G007', 'Crime'), ('G008', 'Fantasy'),
        ('G009', 'Biography'), ('G010', 'Family'), ('G011', 'Romcom'), ('G012', 'Documentary')
    ]
    cursor.executemany("INSERT INTO genres (genre_id, name) VALUES (%s, %s)", genres)
    print(f"  [OK] Inserted {len(genres)} genres")

    # --- Media (Bollywood / Indian titles) ---
    # Start with a curated list then expand programmatically.
    base_titles = [
        ('Sholay', 1975, 'Movie'), ('Dilwale Dulhania Le Jayenge', 1995, 'Movie'),
        ('Sacred Games', 2018, 'Series'), ('Mirzapur', 2018, 'Series'), ('3 Idiots', 2009, 'Movie'),
        ('Kabhi Khushi Kabhie Gham', 2001, 'Movie'), ('Brahmastra: Part One – Shiva', 2022, 'Movie'),
        ('RRR', 2022, 'Movie'), ('Pathaan', 2023, 'Movie'), ('Jawan', 2023, 'Movie'),
        ('Baahubali: The Beginning', 2015, 'Movie'), ('Baahubali: The Conclusion', 2017, 'Movie'),
        ('K.G.F: Chapter 1', 2018, 'Movie'), ('K.G.F: Chapter 2', 2022, 'Movie'),
        ('Pushpa: The Rise', 2021, 'Movie'), ('Paatal Lok', 2020, 'Series'), ('Kota Factory', 2019, 'Series'),
        ('Dev DD', 2017, 'Series'), ('The Married Woman', 2021, 'Series')
    ]

    # Extra popular Indian titles to bulk up the DB (many entries)
    extra_titles = [
        'Don', 'Guide', 'Mother India', 'Mughal-e-Azam', 'Anand', 'Zindagi Na Milegi Dobara',
        'Lagaan', 'Drishyam', 'Andhadhun', 'Tumbbad', 'Article 15', 'Queen', 'Piku', 'Barfi!',
        'Bhaag Milkha Bhaag', 'A Wednesday', 'Black Friday', 'Gully Boy', 'Madras Cafe', 'Dear Zindagi',
        'Swades', 'Kahaani', 'Taare Zameen Par', 'My Name Is Khan', 'Kal Ho Naa Ho', 'Rock On!!',
        'Hero', 'Omkara', 'Devdas', 'Haider', 'Haathi Mere Saathi', 'Ek Tha Tiger', 'Dangal',
        'Secret Superstar', 'Bajrangi Bhaijaan', 'Sultan', 'Padmaavat', 'Tamasha', 'Wake Up Sid',
        'Stree', 'Badhaai Ho', 'Article 15', 'Kesari', 'Rang De Basanti'
    ]

    media = []
    idx = 1
    used_placeholders = []

    # add base titles first
    for t, year, mtype in base_titles:
        media_id = f'M{idx:04d}'
        poster = _tmdb_search_poster(t, 'movie' if mtype == 'Movie' else 'tv') or f'https://example.com/{t.replace(" ", "_").lower()}.jpg'
        if poster and poster.startswith('https://example.com'):
            used_placeholders.append(poster)
        avg_rating = round(random.uniform(6.0, 9.5), 1)
        age_rating = random.choice(['U', 'U/A 13+', 'A'])
        description = f'{t} - description placeholder.'
        media.append((media_id, t, description, year, mtype, age_rating, poster, avg_rating))
        idx += 1
        time.sleep(0.1)

    # add many extra titles programmatically (mix movies and series)
    for t in extra_titles:
        mtype = 'Movie' if random.random() > 0.2 else 'Series'
        media_id = f'M{idx:04d}'
        year = 1980 + (idx % 40)
        poster = _tmdb_search_poster(t, 'movie' if mtype == 'Movie' else 'tv') or f'https://example.com/{t.replace(" ", "_").lower()}.jpg'
        if poster and poster.startswith('https://example.com'):
            used_placeholders.append(poster)
        avg_rating = round(random.uniform(5.5, 9.2), 1)
        age_rating = random.choice(['U', 'U/A 13+', 'A'])
        description = f'{t} - auto-generated seed description.'
        media.append((media_id, t, description, year, mtype, age_rating, poster, avg_rating))
        idx += 1
        time.sleep(0.05)

    # generate additional synthetic entries to make DB much larger (total ~120 media)
    while len(media) < 120:
        t = f'Indie Title {len(media)+1}'
        mtype = 'Movie' if random.random() > 0.3 else 'Series'
        media_id = f'M{idx:04d}'
        year = 1970 + (idx % 55)
        poster = None
        # try TMDB for more realistic titles occasionally
        if random.random() > 0.7:
            poster = _tmdb_search_poster(t, 'movie' if mtype == 'Movie' else 'tv')
        if not poster:
            poster = f'https://example.com/{t.replace(" ", "_").lower()}.jpg'
            used_placeholders.append(poster)
        avg_rating = round(random.uniform(4.5, 8.8), 1)
        age_rating = random.choice(['U', 'U/A 13+', 'A'])
        description = f'{t} - synthetic seed.'
        media.append((media_id, t, description, year, mtype, age_rating, poster, avg_rating))
        idx += 1

    cursor.executemany("""
        INSERT INTO Media (media_id, title, description, release_year, media_type, age_rating, poster_image_url, average_rating)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, media)
    print(f"  [OK] Inserted {len(media)} media items (placeholders used for {len(used_placeholders)} posters)")

    # --- People (actors / personalities) ---
    base_people = [
        ('Amitabh Bachchan', date(1942, 10, 11)), ('Shah Rukh Khan', date(1965, 11, 2)),
        ('Salman Khan', date(1965, 12, 27)), ('Deepika Padukone', date(1986, 1, 5)),
        ('Alia Bhatt', date(1993, 3, 15)), ('Ranveer Singh', date(1985, 7, 6)),
        ('Kareena Kapoor Khan', date(1980, 9, 21)), ('Priyanka Chopra', date(1982, 7, 18)),
        ('Akshay Kumar', date(1967, 9, 9)), ('Katrina Kaif', date(1983, 7, 16)),
        ('Aamir Khan', date(1965, 3, 14)), ('Anushka Sharma', date(1988, 5, 1)),
        ('Varun Dhawan', date(1987, 4, 24)), ('Sidharth Malhotra', date(1985, 1, 16)),
        ('Kiara Advani', date(1992, 7, 31)), ('Rajkummar Rao', date(1984, 8, 31)),
        ('Vicky Kaushal', date(1988, 5, 16)), ('Ayushmann Khurrana', date(1984, 9, 14)),
        ('Radhika Apte', date(1985, 9, 7)), ('Pankaj Tripathi', date(1976, 2, 2))
    ]

    extra_people_names = [
        'Nawazuddin Siddiqui', 'Irrfan Khan', 'Mithun Chakraborty', 'Anupam Kher',
        'Naseeruddin Shah', 'Tabu', 'Nandita Das', 'Shabana Azmi', 'Konkona Sen Sharma',
        'Kay Kay Menon', 'Riteish Deshmukh', 'Tusshar Kapoor', 'Sachin Khedekar',
        'Dilip Kumar', 'Dev Anand', 'Saira Banu', 'Zeenat Aman', 'Rekha', 'Madhuri Dixit',
        'Sanjay Dutt', 'Govinda', 'Farhan Akhtar', 'Shilpa Shetty', 'Boman Irani', 'Anil Kapoor',
        'Kamal Haasan', 'Satyajit Ray', 'Sharmila Tagore', 'Jaya Bachchan', 'Smita Patil',
        'Gulzar', 'Manoj Bajpayee', 'Sushant Singh Rajput', 'R. Madhavan', 'Mahesh Babu'
    ]

    people = []
    pid = 1
    used_person_placeholders = []

    # add base people first
    for name, bdate in base_people:
        person_id = f'P{pid:04d}'
        photo = _tmdb_search_person_photo(name) or f'https://example.com/{name.replace(" ", "_").lower()}.jpg'
        if photo and photo.startswith('https://example.com'):
            used_person_placeholders.append(photo)
        people.append((person_id, name, bdate, photo))
        pid += 1
        time.sleep(0.05)

    # add extra people
    for name in extra_people_names:
        person_id = f'P{pid:04d}'
        bdate = date(1980 + (pid % 30), (pid % 12) + 1, ((pid * 7) % 28) + 1)
        photo = _tmdb_search_person_photo(name) or f'https://example.com/{name.replace(" ", "_").lower()}.jpg'
        if photo and photo.startswith('https://example.com'):
            used_person_placeholders.append(photo)
        people.append((person_id, name, bdate, photo))
        pid += 1
        time.sleep(0.05)

    # synthesize more person entries to enlarge DB
    while len(people) < 200:
        name = f'Actor {len(people)+1}'
        person_id = f'P{pid:04d}'
        bdate = date(1970 + (pid % 40), ((pid * 5) % 12) + 1, ((pid * 3) % 28) + 1)
        photo = None
        if random.random() > 0.8:
            photo = _tmdb_search_person_photo(name)
        if not photo:
            photo = f'https://example.com/{name.replace(" ", "_").lower()}.jpg'
            used_person_placeholders.append(photo)
        people.append((person_id, name, bdate, photo))
        pid += 1

    cursor.executemany("INSERT INTO People (person_id, name, birthdate, photo_url) VALUES (%s, %s, %s, %s)", people)
    print(f"  [OK] Inserted {len(people)} people (placeholders used for {len(used_person_placeholders)} photos)")

    # --- Media-Genres: assign 1-3 random genres to each media
    media_ids = [m[0] for m in media]
    genre_ids = [g[0] for g in genres]
    media_genres = []
    for mid in media_ids:
        assigned = random.sample(genre_ids, k=random.randint(1, 3))
        for gid in assigned:
            media_genres.append((mid, gid))
    cursor.executemany("INSERT INTO Media_Genres (media_id, genre_id) VALUES (%s, %s)", media_genres)
    print(f"  [OK] Inserted {len(media_genres)} media-genre relationships")

    # --- Media Cast: randomly assign 2-6 cast members to each media
    valid_person_ids = [p[0] for p in people]
    valid_media_ids = [m[0] for m in media]
    media_cast = []
    for mid in valid_media_ids:
        num_cast = random.randint(2, 6)
        cast_people = random.sample(valid_person_ids, k=min(num_cast, len(valid_person_ids)))
        for pid in cast_people:
            character = f'Character {random.randint(1,500)}'
            media_cast.append((mid, pid, character))
    # dedupe just in case
    media_cast = list({(m, p): (m, p, c) for (m, p, c) in media_cast}.values())
    cursor.executemany("INSERT INTO Media_Cast (media_id, person_id, character_name) VALUES (%s, %s, %s)", media_cast)
    print(f"  [OK] Inserted {len(media_cast)} cast members")

    # --- Episodes: generate episodes for series media automatically
    episodes = []
    eid = 1
    for m in media:
        mid = m[0]
        mtype = m[4]
        if mtype == 'Series':
            seasons = random.randint(1, 4)
            for s in range(1, seasons + 1):
                eps_in_season = random.randint(3, 12)
                for e in range(1, eps_in_season + 1):
                    episode_id = f'E{eid:05d}'
                    title = f'{m[1]} S{s}E{e}'
                    air_date = date(2000 + (eid % 25), ((eid * 3) % 12) + 1, ((eid * 7) % 28) + 1)
                    episodes.append((episode_id, mid, s, e, title, air_date))
                    eid += 1
    if episodes:
        cursor.executemany("""
            INSERT INTO Episodes (episode_id, media_id, season_number, episode_number, title, air_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, episodes)
    print(f"  [OK] Inserted {len(episodes)} episodes")

    # --- Playlists and playlist items ---
    users_list = [u[0] for u in users]
    playlists = []
    playlist_items = []
    plid = 1
    for user in random.sample(users_list, k=min(80, len(users_list))):
        num_playlists = random.randint(1, 4)
        for _ in range(num_playlists):
            pid = f'PL{plid:05d}'
            name = random.choice(['My Favorites', 'Watch Later', 'Top Picks', 'Binge List', 'Family'])
            playlists.append((pid, user, name))
            # add random items
            items = random.sample(valid_media_ids, k=min(random.randint(3, 12), len(valid_media_ids)))
            for m in items:
                playlist_items.append((pid, m))
            plid += 1
    cursor.executemany("INSERT INTO playlist (playlist_id, username, name) VALUES (%s, %s, %s)", playlists)
    cursor.executemany("INSERT INTO Playlist_item (playlist_id, media_id) VALUES (%s, %s)", playlist_items)
    print(f"  [OK] Inserted {len(playlists)} playlists and {len(playlist_items)} playlist items")

    # --- Watchlist items: assign random watchlist entries to many users
    watchlist_items = []
    statuses = ['watching', 'completed', 'planned', 'dropped']
    for user in random.sample(users_list, k=min(120, len(users_list))):
        for m in random.sample(valid_media_ids, k=random.randint(1, 10)):
            status = random.choice(statuses)
            rating = random.randint(6, 10) if status == 'completed' and random.random() > 0.5 else None
            if rating:
                watchlist_items.append((user, m, status, rating))
            else:
                watchlist_items.append((user, m, status))
    # insert
    for item in watchlist_items:
        if len(item) == 4:
            cursor.execute("INSERT INTO Watchlists_item (username, media_id, status, user_rating) VALUES (%s, %s, %s, %s)", item)
        else:
            cursor.execute("INSERT INTO Watchlists_item (username, media_id, status) VALUES (%s, %s, %s)", item)
    print(f"  [OK] Inserted {len(watchlist_items)} watchlist items")

    # --- Series progress: randomly assign last watched episode for some users & series
    valid_episode_ids = [e[0] for e in episodes]
    series_media_ids = [m[0] for m in media if m[4] == 'Series']
    series_progress = []
    for user in random.sample(users_list, k=min(120, len(users_list))):
        for sm in random.sample(series_media_ids, k=min(5, len(series_media_ids))):
            # pick a random episode id from episodes belonging to this series
            eps_for_series = [e[0] for e in episodes if e[1] == sm]
            if not eps_for_series:
                continue
            last_ep = random.choice(eps_for_series)
            series_progress.append((user, sm, last_ep))
    if series_progress:
        cursor.executemany("INSERT INTO Series_Progress_Table (username, media_id, last_watched_episode_id) VALUES (%s, %s, %s)", series_progress)
    print(f"  [OK] Inserted {len(series_progress)} series progress records")

    # --- Reviews: generate many reviews
    reviews = []
    rid = 1
    for user in random.sample(users_list, k=min(200, len(users_list))):
        for m in random.sample(valid_media_ids, k=random.randint(0, 5)):
            review_id = f'R{rid:06d}'
            text = random.choice(['Loved it', 'Average', 'Not my cup of tea', 'Masterpiece', 'Good watch', 'Could be better'])
            rating = random.randint(4, 10)
            reviews.append((review_id, user, m, text, rating))
            rid += 1
    if reviews:
        cursor.executemany("INSERT INTO Reviews_Table (review_id, username, media_id, review_text, rating) VALUES (%s, %s, %s, %s, %s)", reviews)
    print(f"  [OK] Inserted {len(reviews)} reviews")

    # --- Friends: randomly create friend relationships
    friends = []
    for user in random.sample(users_list, k=min(150, len(users_list))):
        others = random.sample([u for u in users_list if u != user], k=min(12, len(users_list)-1))
        for o in others[:random.randint(1, 6)]:
            status = random.choice(['accepted', 'pending', 'blocked'])
            friends.append((user, o, status))
    # dedupe
    unique_friends = list({(a,b): (a,b,s) for (a,b,s) in friends}.values())
    cursor.executemany("INSERT INTO Friends (username_1, username_2, status) VALUES (%s, %s, %s)", unique_friends)
    print(f"  [OK] Inserted {len(unique_friends)} friend relationships")

    # --- Media crew: assign a few crew roles (Director, Writer) from people pool
    roles = ['Director', 'Writer', 'Producer', 'Cinematographer']
    media_crew = []
    for mid in valid_media_ids:
        crew_people = random.sample(valid_person_ids, k=min(3, len(valid_person_ids)))
        for i, pid in enumerate(crew_people):
            role = roles[i % len(roles)]
            media_crew.append((mid, pid, role))
    # dedupe by (media, person, role)
    unique_media_crew = list({(m,p,r): (m,p,r) for (m,p,r) in media_crew}.values())
    cursor.executemany("INSERT INTO Media_Crew (media_id, person_id, role) VALUES (%s, %s, %s)", unique_media_crew)
    print(f"  [OK] Inserted {len(unique_media_crew)} crew members")

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

