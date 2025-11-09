import mysql.connector
from mysql.connector import Error


def create_connection():
    """Connect to MySQL Server"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",  # change if needed
            database="Streamsync"
        )
        if conn.is_connected():
            print("Connected to MySQL Server")
            return conn
    except Error as e:
        print("Connection error:", e)
        return None


def create_database_and_tables(conn):
    """Create fresh Streamsync database and tables"""
    cursor = conn.cursor()
    print("Creating Database and Tables...")


    cursor.execute("DROP DATABASE IF EXISTS Streamsync;")
    cursor.execute("CREATE DATABASE Streamsync;")
    cursor.execute("USE Streamsync;")

    # TABLES
    schema = [
        """
        CREATE TABLE Users (
            username VARCHAR(50) UNIQUE PRIMARY KEY,
            firstname VARCHAR(50) NOT NULL,
            lastname VARCHAR(50),
            DOB DATE NOT NULL,
            email VARCHAR(255) NOT NULL UNIQUE,
            CHECK (email REGEXP '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Za-z]{2,}$'),
            password CHAR(64) NOT NULL,
            role ENUM('user', 'admin', 'moderator') DEFAULT 'user',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """,
        """
        CREATE TABLE Media (
            media_id VARCHAR(10) PRIMARY KEY,
            title VARCHAR(100) NOT NULL,
            description TEXT,
            release_year YEAR,
            media_type VARCHAR(20),
            CHECK (media_type IN ('Movie', 'Series')),
            age_rating ENUM('G','PG','PG-13','NC-17','U','U/A 7+','U/A 13+','U/A 16+','A') DEFAULT 'U',
            poster_image_url VARCHAR(2083),
            average_rating DECIMAL(3,1)
        );
        """,
        """
        CREATE TABLE Genres (
            genre_id VARCHAR(50) PRIMARY KEY,
            name VARCHAR(50) NOT NULL
        );
        """,
        """
        CREATE TABLE People (
            person_id VARCHAR(20) PRIMARY KEY,
            name VARCHAR(40),
            birthdate DATE,
            photo_url VARCHAR(2083)
        );
        """,
        """
        CREATE TABLE Media_Genres (
            media_id VARCHAR(10),
            genre_id VARCHAR(50),
            PRIMARY KEY (media_id, genre_id),
            FOREIGN KEY (media_id) REFERENCES Media(media_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (genre_id) REFERENCES Genres(genre_id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """,
        """
        CREATE TABLE Media_Cast (
            media_id VARCHAR(10),
            person_id VARCHAR(20),
            character_name VARCHAR(100),
            PRIMARY KEY (media_id, person_id),
            FOREIGN KEY (media_id) REFERENCES Media(media_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (person_id) REFERENCES People(person_id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """,
        """
        CREATE TABLE Media_Crew (
            media_id VARCHAR(10),
            person_id VARCHAR(20),
            role VARCHAR(50),
            PRIMARY KEY (media_id, person_id, role),
            FOREIGN KEY (media_id) REFERENCES Media(media_id) ON DELETE CASCADE ON UPDATE CASCADE,
            FOREIGN KEY (person_id) REFERENCES People(person_id) ON DELETE CASCADE ON UPDATE CASCADE
        );
        """,
        """
        CREATE TABLE Activity_Log (
            log_id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50),
            table_name VARCHAR(50),
            operation ENUM('INSERT','UPDATE','DELETE'),
            record_id VARCHAR(100),
            change_details TEXT,
            changed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    ]

    for q in schema:
        cursor.execute(q)

    # TRIGGER
    cursor.execute("DROP TRIGGER IF EXISTS after_media_insert;")
    cursor.execute("""
    CREATE TRIGGER after_media_insert
    AFTER INSERT ON Media
    FOR EACH ROW
    INSERT INTO Activity_Log (username, table_name, operation, record_id, change_details)
    VALUES (CURRENT_USER(), 'Media', 'INSERT', NEW.media_id, CONCAT('Added media: ', NEW.title));
    """)

    conn.commit()
    print("Database and tables created successfully!")


def insert_data(conn):
    """Insert initial sample data"""
    cursor = conn.cursor()
    cursor.execute("USE Streamsync;")
    print("Inserting sample data...")

    # USERS (using SHA2 hashing)
    users = [
        ('shruti123','Shruti','Gupta','2005-06-10','shruti@example.com','shruti@123','admin'),
        ('rajveer99','Rajveer','Singh','2002-03-22','rajveer@gmail.com','rajpass','user'),
        ('aisha07','Aisha','Khan','2004-09-15','aisha@gmail.com','aisha007','user'),
        ('arjun_dev','Arjun','Dev','1999-11-05','arjun.dev@gmail.com','arjunpass','moderator'),
        ('riya_m','Riya','Mehta','2001-07-11','riya.mehta@gmail.com','riya123','user'),
        ('manav_p','Manav','Patel','2000-01-01','manavp@gmail.com','manavpass','user'),
        ('isha_r','Isha','Reddy','2006-05-20','isha@gmail.com','ishapass','user'),
        ('veeraj','Veeraj','Nair','1998-10-29','veeraj@gmail.com','veeraj123','moderator'),
        ('tanvi_s','Tanvi','Sharma','2003-04-10','tanvi.sharma@gmail.com','tanvipass','user'),
        ('omkar_b','Omkar','Bhosale','1995-12-12','omkar.b@gmail.com','omkar123','user')
    ]
    for u in users:
        cursor.execute("""
            INSERT INTO Users (username, firstname, lastname, DOB, email, password, role)
            VALUES (%s,%s,%s,%s,%s,SHA2(%s,256),%s)
        """, (u[0],u[1],u[2],u[3],u[4],u[5],u[6]))

    # GENRES
    genres = [
        ('G001','Drama'),('G002','Romance'),('G003','Thriller'),
        ('G004','Comedy'),('G005','Crime'),('G006','Family'),
        ('G007','Action'),('G008','Mystery'),('G009','Adventure'),('G010','Biopic')
    ]
    cursor.executemany("INSERT INTO Genres (genre_id,name) VALUES (%s,%s)", genres)

    # MEDIA
    media = [
        ('M001','Sacred Games','A gritty Mumbai crime thriller following Sartaj Singh and Ganesh Gaitonde.',2018,'Series','A','https://example.com/sacredgames.jpg',9.1),
        ('M002','The Family Man','A middle-class man secretly working as a world-class spy.',2019,'Series','U/A 16+','https://example.com/familyman.jpg',8.8),
        ('M003','Dangal','A father trains his daughters to become world-class wrestlers.',2016,'Movie','U','https://example.com/dangal.jpg',9.0),
        ('M004','Mimi','A young woman becomes a surrogate mother for a foreign couple.',2021,'Movie','U/A 13+','https://example.com/mimi.jpg',8.1),
        ('M005','Delhi Crime','Based on true events of the 2012 Delhi gang rape case.',2019,'Series','A','https://example.com/delhicrime.jpg',9.2),
        ('M006','Kota Factory','Life of IIT aspirants in Kota, India.',2019,'Series','U/A 13+','https://example.com/kotafactory.jpg',9.3),
        ('M007','Jawan','An emotional action drama starring Shah Rukh Khan as a vigilante.',2023,'Movie','U/A 16+','https://example.com/jawan.jpg',8.5),
        ('M008','3 Idiots','Three friends navigate the pressures of the Indian education system.',2009,'Movie','U/A 13+','https://example.com/3idiots.jpg',9.4),
        ('M009','She','A shy Mumbai policewoman goes undercover to expose a drug cartel.',2020,'Series','A','https://example.com/she.jpg',7.6),
        ('M010','Taare Zameen Par','A dyslexic child discovers learning differently.',2007,'Movie','U','https://example.com/tzpar.jpg',9.5)
    ]
    cursor.executemany("""
        INSERT INTO Media (media_id, title, description, release_year, media_type, age_rating, poster_image_url, average_rating)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s)
    """, media)

    # PEOPLE
    people = [
        ('P001','Shah Rukh Khan','1965-11-02','https://example.com/srk.jpg'),
        ('P002','Aamir Khan','1965-03-14','https://example.com/aamir.jpg'),
        ('P003','Sanya Malhotra','1992-02-25','https://example.com/sanya.jpg'),
        ('P004','Radhika Apte','1985-09-07','https://example.com/radhika.jpg'),
        ('P005','Nawazuddin Siddiqui','1974-05-19','https://example.com/nawaz.jpg'),
        ('P006','Rajkummar Rao','1984-08-31','https://example.com/rajkummar.jpg'),
        ('P007','Priyanka Chopra','1982-07-18','https://example.com/priyanka.jpg'),
        ('P008','Manoj Bajpayee','1969-04-23','https://example.com/manoj.jpg'),
        ('P009','Ishaan Khattar','1995-11-01','https://example.com/ishaan.jpg'),
        ('P010','Nitesh Tiwari','1973-05-01','https://example.com/nitesh.jpg')
    ]
    cursor.executemany("INSERT INTO People (person_id, name, birthdate, photo_url) VALUES (%s,%s,%s,%s)", people)

    # CAST
    cast = [
        ('M001','P005','Ganesh Gaitonde'),('M001','P008','Sartaj Singh'),
        ('M002','P008','Srikant Tiwari'),('M003','P002','Mahavir Singh Phogat'),
        ('M003','P003','Babita Phogat'),('M004','P003','Mimi Rathore'),
        ('M005','P004','Vartika Chaturvedi'),('M006','P006','Jeetu Bhaiya'),
        ('M007','P001','Azad / Vikram Rathore'),('M008','P002','Rancho'),
        ('M009','P004','Bhumika Pardeshi'),('M010','P002','Ram Shankar Nikumbh')
    ]
    cursor.executemany("INSERT INTO Media_Cast (media_id, person_id, character_name) VALUES (%s,%s,%s)", cast)

    # CREW
    crew = [
        ('M001','P005','Director'),('M002','P008','Director'),('M003','P010','Director'),
        ('M004','P010','Director'),('M005','P004','Director'),('M006','P006','Director'),
        ('M007','P001','Producer'),('M008','P010','Director'),('M009','P004','Director'),
        ('M010','P010','Director')
    ]
    cursor.executemany("INSERT INTO Media_Crew (media_id, person_id, role) VALUES (%s,%s,%s)", crew)

    # MEDIA-GENRES
    genres_map = [
        ('M001','G005'),('M002','G007'),('M003','G010'),('M004','G001'),
        ('M005','G005'),('M006','G006'),('M007','G007'),('M008','G004'),
        ('M009','G003'),('M010','G006')
    ]
    cursor.executemany("INSERT INTO Media_Genres (media_id, genre_id) VALUES (%s,%s)", genres_map)

    conn.commit()
    print("All sample data inserted successfully (SHA2-hashed passwords).")


if __name__ == "__main__":
    conn = create_connection()
    if conn:
        create_database_and_tables(conn)
        insert_data(conn)
        conn.close()
        print("Connection closed successfully.")