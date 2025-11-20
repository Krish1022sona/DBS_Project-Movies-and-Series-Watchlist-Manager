# StreamSync - Movies and Series Watchlist Management System
## Database Management Systems – Final Project Report

---

## Abstract

StreamSync is a comprehensive database-driven web application designed to help users track, organize, and discover movies and series content. The system addresses the growing need for personalized content management in the streaming era, where viewers consume content across multiple platforms. Built using MySQL for robust data storage and Streamlit for an interactive web interface, the platform offers features including personalized watchlists, series progress tracking, reviews and ratings, and social connectivity through friend networks. The system implements a relational database with 14 interconnected tables, supporting role-based access control for users, moderators, and administrators. StreamSync successfully demonstrates practical database concepts including complex queries, triggers, transaction management, and real-world application deployment.

---

## 1. Introduction

### Real-World Problem
In today's digital entertainment landscape, users consume content from multiple streaming platforms, making it challenging to track what they've watched, maintain watchlists, and discover new content. Traditional streaming services lack comprehensive cross-platform tracking and social features for sharing recommendations with friends. Users often forget which episode they last watched in a series or lose track of movies they wanted to watch later.

### Motivation
StreamSync was developed to create a centralized platform where users can:
- Track their viewing progress across all series with episode-level accuracy
- Organize content into custom playlists for different moods or genres
- Connect with friends to share and discover new content through recommendations
- Write and read reviews to make informed viewing decisions
- Maintain a complete history of their entertainment consumption

### Scope of the Project
The project encompasses:
- **User Management:** Secure authentication with role-based access (user, moderator, admin)
- **Content Library:** Comprehensive media database with movies and series information
- **Personal Organization:** Custom playlists and series progress tracking
- **Social Features:** Friend connections, mutual friend discovery, and shared recommendations
- **Review System:** User ratings and detailed reviews for all content
- **Administrative Controls:** Database management tools and activity logging

### Target Users
- **Regular Users:** Track personal viewing habits and organize content
- **Moderators:** Manage database integrity, moderate reviews, and update content
- **Administrators:** Oversee system operations, manage users, and monitor database handlers

### Key Objectives
1. Design a normalized relational database for efficient data storage
2. Implement comprehensive user authentication with password hashing
3. Create intuitive interfaces for content discovery and management
4. Enable social connectivity for content recommendations
5. Provide administrative tools for system maintenance and monitoring
6. Ensure data integrity through constraints, triggers, and transaction management

---

## 2. System Analysis & Design

### 2.1 Requirements Summary

**Functional Requirements:**
- User registration, login, and profile management with SHA-256 password hashing
- Browse and search movies/series with multi-criteria filtering (genre, people, type, rating)
- Create, manage, and delete custom playlists with multiple media items
- Track series viewing progress with episode-level granularity
- Write, edit, and delete reviews with 1-10 star ratings
- Send, accept, and manage friend requests with pending/accepted status
- View friend profiles and discover mutual connections
- Admin dashboard for user role management and system statistics
- Database handler interface for CRUD operations on all tables
- Activity logging for comprehensive audit trails
- Media details pages with cast, crew, genres, and episode information

**Non-Functional Requirements:**
- **Security:** SHA-256 password hashing, SQL injection prevention through parameterized queries
- **Performance:** Database connection pooling, indexed queries on foreign keys
- **Scalability:** Designed to support 1000+ concurrent users
- **Usability:** Responsive UI with intuitive navigation and modern design
- **Reliability:** Transaction management with automatic rollback on errors
- **Maintainability:** Modular code structure with clear separation of concerns
- **Data Integrity:** Foreign key constraints with CASCADE operations for referential integrity

### 2.2 Entities & Relationships

**Core Entities:**

1. **Users:** Stores user account information (username, firstname, lastname, email, password, DOB, role)
2. **Media:** Contains movies and series metadata (media_id, title, description, release_year, media_type, age_rating, poster_image_url, average_rating)
3. **Genres:** Categorizes media content (genre_id, name) - Action, Drama, Thriller, etc.
4. **People:** Stores information about actors, directors, and crew members (person_id, name, birthdate, photo_url)
5. **Episodes:** Tracks individual episodes for series (episode_id, media_id, season_number, episode_number, title, air_date)
6. **Playlist:** User-created collections of media items (playlist_id, username, name, created_at)
7. **Playlist_item:** Junction table linking playlists to media (playlist_id, media_id)
8. **Watchlists_item:** Tracks user's personal watchlist with status and ratings (username, media_id, status, user_rating)
9. **Series_Progress_Table:** Records viewing progress for series (username, media_id, last_watched_episode_id, last_watched_at)
10. **Reviews_Table:** Stores user reviews and ratings (review_id, username, media_id, review_text, rating, created_at, updated_at)
11. **Friends:** Manages friendship connections (username_1, username_2, status, created_at)
12. **Media_Genres:** Junction table linking media to multiple genres (media_id, genre_id)
13. **Media_Cast:** Links actors to media with character information (media_id, person_id, character_name)
14. **Media_Crew:** Links crew members to media with role information (media_id, person_id, role)
15. **Activity_Log:** Audit trail for all database modifications (log_id, username, table_name, operation, record_id, change_details, changed_at)

### 2.3 ER Diagram

**[INSERT ER DIAGRAM IMAGE HERE - E-R Model/E-R Model DBS.drawio.png]**

*Figure 1: Entity-Relationship Diagram showing all entities, attributes, primary keys, foreign keys, and relationships with cardinalities.*

**Key Relationships:**
- Users to Playlist (1:N) - One user can create multiple playlists
- Media to Episodes (1:N) - One series contains multiple episodes
- Users to Friends (M:N) - Many-to-many friendship relationships (self-referencing)
- Media to Genres (M:N) - Many-to-many through Media_Genres junction table
- People to Media (M:N) - Through Media_Cast and Media_Crew tables
- Users to Series_Progress_Table (1:N) - Users track progress for multiple series
- Users to Reviews_Table (1:N) - Users can write multiple reviews
- Media to Reviews_Table (1:N) - Each media item can have multiple reviews

### 2.4 Database Schema Design & Normalization

**Normalization Approach:**

The database was designed directly in Third Normal Form (3NF) from the beginning, eliminating the need for step-by-step normalization. The schema inherently satisfies:

- **1NF:** All attributes contain atomic values with no repeating groups
- **2NF:** All non-key attributes are fully dependent on primary keys
- **3NF:** No transitive dependencies exist between non-key attributes

**Key Design Decisions:**

**Primary Tables:**
- **Users:** Primary Key = username (VARCHAR 50), unique email with format validation
- **Media:** Primary Key = media_id (VARCHAR 10), CHECK constraint for media_type (Movie/Series)
- **Genres:** Primary Key = genre_id (VARCHAR 50)
- **People:** Primary Key = person_id (VARCHAR 20)
- **Episodes:** Primary Key = episode_id (VARCHAR 50), Foreign Key to Media with CASCADE delete

**Junction Tables:**
- **Media_Genres:** Composite Primary Key (media_id, genre_id)
- **Media_Cast:** Composite Primary Key (media_id, person_id)
- **Media_Crew:** Composite Primary Key (media_id, person_id, role)
- **Playlist_item:** Composite Primary Key (playlist_id, media_id)
- **Friends:** Composite Primary Key (username_1, username_2)

**Tracking Tables:**
- **Watchlists_item:** Composite Primary Key (username, media_id), includes status and optional rating
- **Series_Progress_Table:** Composite Primary Key (username, media_id), tracks last_watched_episode_id
- **Reviews_Table:** Primary Key = review_id (VARCHAR 10), unique constraint on (username, media_id)
- **Activity_Log:** Primary Key = log_id (AUTO_INCREMENT), logs all database operations

**Referential Integrity:**
- All foreign keys implement ON DELETE CASCADE for automatic cleanup
- ON UPDATE CASCADE ensures consistency when primary keys change
- CHECK constraints enforce valid data ranges (ratings 1-10, status enums)
- UNIQUE constraints prevent duplicate data (email, review per user per media)

---

## 3. Database Implementation

### 3.1 Database Schema (DDL Overview)

**Database Structure:**
- **Total Tables:** 15 tables with comprehensive relational integrity
- **Primary Keys:** Mix of natural keys (username) and surrogate keys (media_id, review_id)
- **Foreign Keys:** 25+ foreign key relationships with CASCADE operations
- **Indexes:** Strategic indexes on foreign key columns (media_id, username, genre_id, person_id) for query optimization

**Key Constraints:**
- **UNIQUE:** Email addresses, composite keys for junction tables, (username, media_id) in Reviews_Table
- **CHECK:** Email regex validation (`^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$`), rating ranges (1-10), media_type IN ('Movie', 'Series'), status values, age ratings
- **NOT NULL:** Critical fields like passwords, usernames, titles, email
- **DEFAULT:** CURRENT_TIMESTAMP for created_at/updated_at fields, 'user' for role, 'U' for age_rating
- **ENUM:** Role (user/admin/moderator), media_type (Movie/Series), friend status (pending/accepted/blocked), age_rating (G/PG/PG-13/NC-17/U/U/A 7+/U/A 13+/U/A 16+/A)

**Triggers Implemented:**

The database includes triggers for automatic rating calculations and activity logging:

```sql
-- Automatic average rating update when review is inserted
DELIMITER $$
CREATE TRIGGER after_review_insert
AFTER INSERT ON Reviews_Table
FOR EACH ROW
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

-- Similar triggers exist for UPDATE and DELETE operations
```

Additional triggers handle activity logging for Media table operations (INSERT, UPDATE, DELETE) to maintain comprehensive audit trails.

### 3.2 Sample Data (DML)

The database is populated with realistic Indian/Bollywood entertainment data through the `reset_database.py` script:

**Sample Data Statistics:**
- **152 Users:** Including admin, moderator, and 150 regular users with varied profiles
- **91 Media Items:** Mix of popular Bollywood movies and Indian web series (Sholay, 3 Idiots, Sacred Games, Mirzapur, etc.)
- **16 Genres:** Covering all major categories (Action, Drama, Romance, Thriller, Comedy, etc.)
- **87 People:** Renowned actors, directors, and crew (Shah Rukh Khan, Aamir Khan, Rajkumar Hirani, etc.)
- **500+ Episodes:** Sample episodes across multiple series with proper season/episode numbering
- **100+ Playlists:** User-created collections with varied themes
- **1000+ Relationships:** Across junction tables (cast assignments, crew roles, genre mappings, playlist items)
- **200+ Reviews:** User-generated ratings and review texts
- **140+ Friendships:** Friend connections with accepted and pending status

**Sample Data Excerpt:**

| username | firstname | lastname | email | role |
|----------|-----------|----------|-------|------|
| admin | Admin | User | admin@streamsync.com | admin |
| moderator | Mod | User | mod@streamsync.com | moderator |
| user001 | User001 | Demo | user001@example.com | user |

| media_id | title | media_type | release_year | average_rating |
|----------|-------|------------|--------------|----------------|
| M0001 | Sholay | Movie | 1975 | 8.2 |
| M0002 | Mughal-e-Azam | Movie | 1960 | 8.1 |
| M0067 | Sacred Games | Series | 2018 | 8.6 |
| M0068 | Mirzapur | Series | 2018 | 8.4 |

**[INSERT SCREENSHOT: MySQL Workbench showing sample data from Users and Media tables]**

### 3.3 Tools & Environment

**Database Management:**
- **MySQL Server 8.0:** Primary database engine with InnoDB storage
- **MySQL Connector/Python 9.5.0:** Python database driver for connectivity
- **Connection Pooling:** Implemented for optimized performance and resource management

**Application Framework:**
- **Python 3.8+:** Core programming language
- **Streamlit 1.51.0:** Modern web application framework for rapid UI development
- **Hashlib:** Built-in Python library for SHA-256 password encryption
- **Pandas 2.3.3:** Data manipulation and display in tabular format

**Development Environment:**
- **Operating System:** Cross-platform support (Windows/Linux/macOS)
- **IDE:** VS Code / PyCharm for development
- **Version Control:** Git for source code management
- **Database Client:** MySQL Workbench 8.0 CE for schema design and testing

**Configuration Management:**
- Session-based password storage for database credentials
- Modular function architecture for maintainability
- Environment-specific configuration support

---

## 4. Query Module

### 4.1 Query List

**Category 1: Basic SELECT with WHERE**

**Query 1 – User Authentication**
```sql
SELECT username, role 
FROM Users 
WHERE username = %s AND password = SHA2(%s, 256);
```
*Purpose: Secure user login with hashed password comparison*

**Query 2 – Media Search by Title**
```sql
SELECT media_id, title, description, release_year, media_type, average_rating
FROM Media
WHERE title LIKE %s
ORDER BY average_rating DESC, title ASC;
```
*Purpose: Search functionality with relevance sorting*

**Category 2: Aggregations (COUNT, AVG, MAX, MIN)**

**Query 3 – User Dashboard Statistics**
```sql
SELECT 
    (SELECT COUNT(*) FROM playlist WHERE username = %s) as watchlists,
    (SELECT COUNT(*) FROM Series_Progress_Table WHERE username = %s) as series,
    (SELECT COUNT(*) FROM Friends 
     WHERE (username_1 = %s OR username_2 = %s) AND status = 'accepted') as friends;
```
*Purpose: Generate user engagement metrics for dashboard*

**Query 4 – Top Rated Content**
```sql
SELECT media_id, title, media_type, average_rating
FROM Media
WHERE average_rating IS NOT NULL
ORDER BY average_rating DESC, title ASC
LIMIT 5;
```
*Purpose: Display highest-rated content for recommendations*

**Category 3: GROUP BY with HAVING**

**Query 5 – Playlist Summary**
```sql
SELECT p.playlist_id, p.name, p.created_at,
       COUNT(pi.media_id) as item_count
FROM playlist p
LEFT JOIN Playlist_item pi ON p.playlist_id = pi.playlist_id
WHERE p.username = %s
GROUP BY p.playlist_id, p.name, p.created_at
ORDER BY p.created_at DESC;
```
*Purpose: List user's playlists with item counts*

**Query 6 – Genre Popularity**
```sql
SELECT g.name, COUNT(mg.media_id) as media_count
FROM genres g
JOIN Media_Genres mg ON g.genre_id = mg.genre_id
GROUP BY g.genre_id, g.name
HAVING COUNT(mg.media_id) >= 3
ORDER BY media_count DESC;
```
*Purpose: Analyze which genres have the most content*

**Category 4: Complex Joins**

**Query 7 – Series Progress with Episode Details**
```sql
SELECT sp.media_id, m.title, m.poster_image_url,
       sp.last_watched_episode_id, e.season_number, e.episode_number,
       e.title as episode_title, sp.last_watched_at
FROM Series_Progress_Table sp
JOIN Media m ON sp.media_id = m.media_id
LEFT JOIN Episodes e ON sp.last_watched_episode_id = e.episode_id
WHERE sp.username = %s AND m.media_type = 'Series'
ORDER BY sp.last_watched_at DESC;
```
*Purpose: Track user's current position in each series*

**Query 8 – Media with Cast and Crew**
```sql
SELECT m.*, 
       mc.person_id, p.name, mc.character_name
FROM Media m
LEFT JOIN Media_Cast mc ON m.media_id = mc.media_id
LEFT JOIN People p ON mc.person_id = p.person_id
WHERE m.media_id = %s;
```
*Purpose: Retrieve complete media details with cast information*

**Query 9 – Reviews for Media**
```sql
SELECT r.review_id, r.username, u.firstname, u.lastname, r.review_text,
       r.rating, r.created_at, r.updated_at
FROM Reviews_Table r
JOIN Users u ON r.username = u.username
WHERE r.media_id = %s
ORDER BY r.updated_at DESC, r.created_at DESC;
```
*Purpose: Display all reviews for a specific media item*

**Category 5: Subqueries**

**Query 10 – Personalized Recommendations**
```sql
SELECT DISTINCT m.media_id, m.title, m.poster_image_url, 
       m.average_rating, m.media_type
FROM Media m
LEFT JOIN Watchlists_item wi ON m.media_id = wi.media_id AND wi.username = %s
WHERE wi.media_id IS NULL
ORDER BY m.average_rating DESC
LIMIT 10;
```
*Purpose: Recommend unwatched content based on ratings*

**Query 11 – Mutual Friends Discovery**
```sql
SELECT DISTINCT u.username, u.firstname, u.lastname
FROM Friends f1
JOIN Friends f2 ON (f1.username_1 = f2.username_1 OR f1.username_1 = f2.username_2 
                    OR f1.username_2 = f2.username_1 OR f1.username_2 = f2.username_2)
JOIN Users u ON ((f1.username_1 = u.username OR f1.username_2 = u.username)
                 AND (f2.username_1 = u.username OR f2.username_2 = u.username))
WHERE ((f1.username_1 = %s OR f1.username_2 = %s) AND f1.status = 'accepted')
  AND ((f2.username_1 = %s OR f2.username_2 = %s) AND f2.status = 'accepted')
  AND u.username NOT IN (%s, %s);
```
*Purpose: Find common friends between two users*

**Query 12 – Activity Monitoring**
```sql
SELECT * FROM Activity_Log 
ORDER BY changed_at DESC 
LIMIT 50;
```
*Purpose: Administrative audit trail of recent changes*

### 4.2 Query Output Screenshots

**[INSERT SCREENSHOT 1: Search Results - Explore page showing filtered media cards with titles, ratings, release years, and descriptions in a grid layout]**

**[INSERT SCREENSHOT 2: User Dashboard - Home page displaying statistics cards (watchlists, series, friends counts), continue watching section, and recommendations]**

**[INSERT SCREENSHOT 3: Watchlist Details - Playlist page showing list of media items with poster images, titles, and remove buttons]**

**[INSERT SCREENSHOT 4: Series Progress - Table showing multiple series with episode information (S1E5 format) and last watched timestamps]**

**[INSERT SCREENSHOT 5: Admin Activity Log - Table displaying recent database operations with username, table name, operation type, and timestamps]**

---

## 5. User Interface / Frontend

### 5.1 Interface Description

**Technology Stack:**
- **Framework:** Streamlit 1.51.0 for rapid web application development with Python
- **Styling:** Custom CSS with gradient backgrounds, modern card layouts, and responsive design
- **Interactivity:** Session state management for seamless navigation and data persistence
- **Responsiveness:** Column-based layouts adapting to different screen sizes

**User Interaction Flow:**

1. **Landing Page:** 
   - Feature showcase with three main sections (Vast Library, Custom Playlists, Social Features)
   - Login and Register buttons in sidebar
   - Database password setup section

2. **Authentication:** 
   - Login form with username/password fields
   - Registration form with validation (firstname, lastname, email, DOB, password confirmation)
   - SHA-256 password hashing for security

3. **User Dashboard (5 Main Sections):**
   - **Home:** Statistics cards, continue watching, recommendations, top-rated content
   - **Explore:** Advanced search with multi-criteria filters (title, cast, crew, genre, type, rating)
   - **Watchlist:** Create/manage playlists, add/remove items, view playlist details
   - **Series Progress:** Track episode progress, update watched episodes, remove series
   - **Friends:** View friends list, send/accept requests, view friend profiles, mutual friends

4. **Media Details Page:**
   - Full media information (title, description, ratings, genres, release year)
   - Cast and crew sections with roles
   - Episode list for series
   - User review section with add/edit/delete functionality
   - Community reviews display

5. **Admin Dashboard:**
   - System metrics (total users, media, handlers)
   - Activity log monitoring with table filtering
   - Database handler management

6. **Moderator Interface:**
   - All admin features plus database table management
   - CRUD operations with Insert/Update/Delete tabs
   - Direct table data viewing and editing

**Key UI Features:**
- Session-based authentication with automatic role-based redirection
- Real-time search with dynamic filtering
- Modal-style detail pages with back navigation
- Confirmation patterns for destructive actions
- Success/error toast notifications
- Gradient backgrounds and card-based layouts
- Emoji-enhanced navigation icons for better UX
- Consistent color scheme (purple/pink gradients for headers)

### 5.2 UI Screenshots

**[INSERT SCREENSHOT 1: Landing Page - Full page view showing gradient header "StreamSync - Track. Save. Discover", feature sections with images, and call-to-action button]**

**[INSERT SCREENSHOT 2: User Dashboard Home - Shows metrics cards (3 columns), continue watching section, top-rated content grid, and recent watchlists]**

**[INSERT SCREENSHOT 3: Explore/Search Page - Search bar at top, filter options (Movies/Series checkboxes, genre multiselect, people filters), grid of 3x3 media result cards]**

**[INSERT SCREENSHOT 4: Media Details Page - Large view showing movie/series information, cast section with 4-column grid, crew section, and reviews below]**

**[INSERT SCREENSHOT 5: Watchlist Management - Two-column layout showing playlist list on left, selected playlist details on right with media items]**

**[INSERT SCREENSHOT 6: Series Progress Interface - List of series cards showing poster, title, last watched episode (S2E5 format), and update/remove buttons]**

**[INSERT SCREENSHOT 7: Friends Page - Split view with friends list on left showing user profiles, and search/add section on right with suggested users]**

**[INSERT SCREENSHOT 8: Admin Dashboard - Top metrics in 3 columns, activity log table below with filtering dropdown, and database handlers section]**

---

## 6. Conclusion & Future Scope

### 6.1 Achievements

StreamSync successfully demonstrates a complete database-driven application addressing real-world content tracking needs. The project achieves:

**Technical Accomplishments:**
- **Robust Database Design:** 15 normalized tables with comprehensive relationships, constraints, and referential integrity
- **Secure Authentication:** SHA-256 password hashing with role-based access control (Admin, Moderator, User)
- **Rich Functionality:** Personal playlists, episode-level series tracking, review system, and social friend network
- **Administrative Tools:** Complete database management interface with CRUD operations and activity logging
- **User-Friendly Interface:** Modern, intuitive UI with gradient designs and responsive layouts
- **Real-World Applicability:** Solves actual problems for streaming content consumers

**DBMS Concepts Demonstrated:**
- Complex relational schema design with junction tables
- Transaction management with automatic rollback on errors
- Triggers for automated rating calculations and activity logging
- Optimized queries with joins, subqueries, and aggregations
- Connection pooling for performance optimization
- Data integrity through constraints and cascading operations
- Comprehensive indexing strategy for query performance

The application successfully handles realistic data volumes (150+ users, 90+ media items, 500+ episodes, 1000+ relationships) and demonstrates scalability through efficient query design.

### 6.2 Limitations

**Current Constraints:**
- **Database Technology:** Limited to MySQL with no NoSQL integration for flexible schemas
- **Real-Time Features:** No WebSocket support for live notifications or updates
- **Search Capability:** Basic pattern matching; lacks full-text search on descriptions and reviews
- **Collaborative Features:** No multi-user collaborative playlists or watch parties
- **Data Management:** Activity log grows unbounded without archival or cleanup strategy
- **Media Content:** URL-only poster storage; no built-in image upload functionality
- **Error Recovery:** Limited network failure handling and retry mechanisms
- **Performance:** No caching layer for frequently accessed data
- **Analytics:** Basic statistics only; no advanced user behavior analysis

### 6.3 Future Enhancements

**Technical Improvements:**

1. **Advanced Search Engine:**
   - Elasticsearch integration for full-text search across all media metadata
   - Fuzzy matching for typo-tolerant searches
   - Search suggestions and autocomplete

2. **Machine Learning Integration:**
   - Collaborative filtering for personalized recommendations
   - Content-based filtering using genre and cast preferences
   - Watch time prediction algorithms

3. **Real-Time Features:**
   - WebSocket implementation for live friend activity feeds
   - Push notifications for new episodes and friend recommendations
   - Real-time watch party synchronization

4. **Performance Optimization:**
   - Redis caching layer for hot data (top-rated content, user sessions)
   - Database read replicas for query load distribution
   - CDN integration for static content delivery

5. **Mobile & API Development:**
   - RESTful API for third-party integrations
   - React Native or Flutter mobile applications
   - OAuth integration for social login

**Feature Additions:**

1. **Enhanced Social Features:**
   - Activity feed showing friend reviews and watch history
   - Group playlists with collaborative editing
   - Virtual watch parties with synchronized playback
   - Chat and discussion threads for media

2. **Advanced Review System:**
   - Like/dislike functionality on reviews
   - "Helpful" votes and review ranking
   - Spoiler tags and content warnings
   - Review moderation tools

3. **Content Discovery:**
   - Integration with TMDb, IMDb APIs for metadata
   - Automatic import from streaming services
   - Trending content algorithms
   - "Because you watched..." recommendations

4. **Gamification:**
   - Achievement badges for viewing milestones
   - User levels based on reviews and activity
   - Leaderboards for top contributors
   - Seasonal watching challenges

5. **Analytics Dashboard:**
   - Viewing time tracking and statistics
   - Genre distribution charts
   - Yearly summaries and wrap-ups
   - Friend comparison statistics

**Scalability Considerations:**
- Microservices architecture for independent service scaling
- Database sharding for horizontal scalability
- Message queue integration (RabbitMQ/Kafka) for async operations
- Comprehensive monitoring with Prometheus and Grafana
- Automated testing and CI/CD pipeline

StreamSync provides a solid foundation for a comprehensive entertainment tracking platform with clear pathways for enhancement and scaling to meet growing user needs.

---

## 7. References

1. **MySQL Documentation**
   - MySQL 8.0 Reference Manual: https://dev.mysql.com/doc/refman/8.0/en/
   - MySQL Connector/Python Developer Guide: https://dev.mysql.com/doc/connector-python/en/

2. **Python Framework Documentation**
   - Streamlit Documentation: https://docs.streamlit.io/
   - Pandas Documentation: https://pandas.pydata.org/docs/
   - Python Hashlib Library: https://docs.python.org/3/library/hashlib.html

3. **Database Design Resources**
   - Database System Concepts (7th Edition) by Silberschatz, Korth, and Sudarshan
   - SQL Performance Explained by Markus Winand

4. **Web Development Resources**
   - MDN Web Docs (CSS and HTML): https://developer.mozilla.org/
   - Streamlit Community Forum: https://discuss.streamlit.io/

5. **Security Best Practices**
   - OWASP SQL Injection Prevention: https://cheatsheetseries.owasp.org/
   - NIST Password Guidelines: https://pages.nist.gov/800-63-3/

---