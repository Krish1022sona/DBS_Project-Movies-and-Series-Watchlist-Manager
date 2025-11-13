import streamlit as st
import mysql.connector
from mysql.connector import Error
import hashlib
from datetime import datetime
import pandas as pd
import toml
import os

st.markdown("""
    <style>
    .header-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
    }
    .stButton > button {
        width: 100%;
        border-radius: 8px;
        border: none;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'page' not in st.session_state:
    st.session_state.page = "Landing"
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'selected_table' not in st.session_state:
    st.session_state.selected_table = ""
if 'handlers' not in st.session_state:
    st.session_state.handlers = []
if 'selected_nav' not in st.session_state:
    st.session_state.selected_nav = "Home"
if 'user_role' not in st.session_state:
    st.session_state.user_role = "user"
if 'db_conn' not in st.session_state:
    st.session_state.db_conn = None
if 'selected_media_id' not in st.session_state:
    st.session_state.selected_media_id = None
if 'selected_friend' not in st.session_state:
    st.session_state.selected_friend = None
if 'selected_playlist_id' not in st.session_state:
    st.session_state.selected_playlist_id = None
if 'update_series_mode' not in st.session_state:
    st.session_state.update_series_mode = False
if 'add_to_watchlist_mode' not in st.session_state:
    st.session_state.add_to_watchlist_mode = False
if 'add_to_watchlist_id' not in st.session_state:
    st.session_state.add_to_watchlist_id = None
if 'selected_handler_user' not in st.session_state:
    st.session_state.selected_handler_user = None
if 'db_add_user' not in st.session_state:
    st.session_state.db_add_user = False

def load_db_config():
    """Load database configuration from secrets.toml"""
    try:
        secrets_path = os.path.join(os.path.dirname(__file__), '.streamlit', 'secrets.toml')
        with open(secrets_path, 'r') as f:
            secrets = toml.load(f)
        return secrets['db']
    except Exception:
        return {'host': 'localhost', 'user': 'root', 'password': '', 'database': 'Streamsync'}

def get_db_connection():
    """Get database connection with connection pooling"""
    try:
        if st.session_state.db_conn is None or not st.session_state.db_conn.is_connected():
            db_config = load_db_config()
            st.session_state.db_conn = mysql.connector.connect(
                host=db_config['host'],
                user=db_config['user'],
                password=db_config['password'],
                database=db_config['database'],
                autocommit=False
            )
        return st.session_state.db_conn
    except Error as e:
        st.error(f"Database connection error: {e}")
        return None

def hash_password(password):
    """Hash password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def execute_query(query, params=None, fetch=True):
    """Execute database query safely"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(query, params or ())
        if fetch:
            result = cursor.fetchall()
            cursor.close()
            return result
        else:
            conn.commit()
            cursor.close()
            return True
    except Error as e:
        conn.rollback()
        st.error(f"Query error: {e}")
        return None

def log_activity(table_name, operation, record_id, details, username=None):
    """Log activity into Activity_Log table"""
    actor = username or st.session_state.get('username') or 'system'
    try:
        return execute_query(
            """INSERT INTO Activity_Log (username, table_name, operation, record_id, change_details)
               VALUES (%s, %s, %s, %s, %s)""",
            (actor, table_name, operation, str(record_id), details),
            fetch=False
        )
    except Exception:
        # Avoid breaking main flow if logging fails
        return None

def authenticate_user(username, password):
    """Authenticate user login"""
    hashed = hash_password(password)
    query = "SELECT username, role FROM Users WHERE username = %s AND password = %s"
    result = execute_query(query, (username, hashed))
    if result and len(result) > 0:
        return result[0]
    return None

def register_user(username, firstname, lastname, email, password, dob, role='user', created_by=None):
    """Register new user"""
    hashed = hash_password(password)
    query = """INSERT INTO Users (username, firstname, lastname, email, password, DOB, role)
               VALUES (%s, %s, %s, %s, %s, %s, %s)"""
    success = execute_query(query, (username, firstname, lastname, email, hashed, dob, role), fetch=False)
    if success:
        log_activity(
            "Users",
            "INSERT",
            username,
            f"User {username} created with role {role}",
            created_by or username
        )
    return success

def get_user_watchlists(username):
    """Get all watchlists for a user"""
    query = """SELECT DISTINCT p.playlist_id, p.name, p.created_at,
               COUNT(pi.media_id) as item_count
               FROM playlist p
               LEFT JOIN Playlist_item pi ON p.playlist_id = pi.playlist_id
               WHERE p.username = %s
               GROUP BY p.playlist_id, p.name, p.created_at
               ORDER BY p.created_at DESC"""
    return execute_query(query, (username,))

def create_watchlist(username, playlist_name):
    """Create new watchlist"""
    playlist_id = f"PL{datetime.now().strftime('%Y%m%d%H%M%S')}"
    query = "INSERT INTO playlist (playlist_id, username, name) VALUES (%s, %s, %s)"
    success = execute_query(query, (playlist_id, username, playlist_name), fetch=False)
    if success:
        log_activity(
            "playlist",
            "INSERT",
            playlist_id,
            f"Playlist '{playlist_name}' created by {username}",
            username
        )
    return success

def get_watchlist_items(playlist_id):
    """Get items in a watchlist"""
    query = """SELECT pi.playlist_id, pi.media_id, m.title, m.media_type, m.poster_image_url, m.average_rating
               FROM Playlist_item pi
               JOIN Media m ON pi.media_id = m.media_id
               WHERE pi.playlist_id = %s"""
    return execute_query(query, (playlist_id,))

def add_to_watchlist(playlist_id, media_id, added_by=None):
    """Add media to watchlist"""
    query = """INSERT INTO Playlist_item (playlist_id, media_id)
               VALUES (%s, %s)
               ON DUPLICATE KEY UPDATE media_id = VALUES(media_id)"""
    success = execute_query(query, (playlist_id, media_id), fetch=False)
    if success:
        log_activity(
            "Playlist_item",
            "INSERT",
            f"{playlist_id}:{media_id}",
            f"Added media {media_id} to playlist {playlist_id}",
            added_by
        )
    return success

def remove_from_watchlist(playlist_id, media_id, removed_by=None):
    """Remove item from watchlist"""
    query = "DELETE FROM Playlist_item WHERE playlist_id = %s AND media_id = %s"
    success = execute_query(query, (playlist_id, media_id), fetch=False)
    if success:
        log_activity(
            "Playlist_item",
            "DELETE",
            f"{playlist_id}:{media_id}",
            f"Removed media {media_id} from playlist {playlist_id}",
            removed_by
        )
    return success

def delete_watchlist(playlist_id, deleted_by=None):
    """Delete a watchlist"""
    query = "DELETE FROM playlist WHERE playlist_id = %s"
    success = execute_query(query, (playlist_id,), fetch=False)
    if success:
        log_activity(
            "playlist",
            "DELETE",
            playlist_id,
            f"Playlist {playlist_id} deleted",
            deleted_by
        )
    return success

def remove_series_progress(username, media_id, removed_by=None):
    """Remove series from progress"""
    query = "DELETE FROM Series_Progress_Table WHERE username = %s AND media_id = %s"
    success = execute_query(query, (username, media_id), fetch=False)
    if success:
        log_activity(
            "Series_Progress_Table",
            "DELETE",
            f"{username}:{media_id}",
            f"Removed series {media_id} from {username}'s progress",
            removed_by or username
        )
    return success

def get_series_progress(username):
    """Get user's series progress"""
    query = """SELECT sp.media_id, m.title, m.poster_image_url,
               sp.last_watched_episode_id, e.season_number, e.episode_number,
               e.title as episode_title, sp.last_watched_at
               FROM Series_Progress_Table sp
               JOIN Media m ON sp.media_id = m.media_id
               LEFT JOIN Episodes e ON sp.last_watched_episode_id = e.episode_id
               WHERE sp.username = %s AND m.media_type = 'Series'
               ORDER BY sp.last_watched_at DESC"""
    return execute_query(query, (username,))

def update_series_progress(username, media_id, episode_id):
    """Update series progress"""
    query = """INSERT INTO Series_Progress_Table (username, media_id, last_watched_episode_id)
               VALUES (%s, %s, %s)
               ON DUPLICATE KEY UPDATE
               last_watched_episode_id = %s, last_watched_at = CURRENT_TIMESTAMP"""
    return execute_query(query, (username, media_id, episode_id, episode_id), fetch=False)

def search_media(query, filters=None):
    """Search media by title and cast"""
    base_query = """SELECT DISTINCT m.media_id, m.title, m.description, m.release_year,
                    m.media_type, m.age_rating, m.poster_image_url, m.average_rating
                    FROM Media m"""
    conditions = []
    params = []
    
    if query:
        search_term = f"%{query}%"
        # Only search title first, then optionally search cast
        conditions.append("m.title LIKE %s")
        params.append(search_term)
        
        # Only join cast if we want cast-based search
        # For now, prioritize title search
        # joins.append("LEFT JOIN Media_Cast mc ON m.media_id = mc.media_id")
        # joins.append("LEFT JOIN People p ON mc.person_id = p.person_id")
        # cast_condition = "(p.name LIKE %s OR mc.character_name LIKE %s)"
        # params.extend([search_term, search_term])
    
    if filters:
        type_conditions = []
        if "Movies" in filters:
            type_conditions.append("m.media_type = 'Movie'")
        if "Series" in filters:
            type_conditions.append("m.media_type = 'Series'")
        if type_conditions:
            conditions.append("(" + " OR ".join(type_conditions) + ")")
    
    if conditions:
        base_query += " WHERE " + " AND ".join(conditions)
    
    base_query += " ORDER BY m.average_rating DESC LIMIT 50"
    return execute_query(base_query, tuple(params) if params else None)

def search_users(query):
    """Search users by username or name"""
    search_term = f"%{query}%"
    query_sql = """SELECT username, firstname, lastname, email
                   FROM Users
                   WHERE username LIKE %s OR firstname LIKE %s OR lastname LIKE %s
                   LIMIT 20"""
    return execute_query(query_sql, (search_term, search_term, search_term))

def user_exists(username):
    """Check if user exists"""
    result = execute_query("SELECT username FROM Users WHERE username = %s", (username,))
    return result and len(result) > 0

def get_user_profile(username):
    """Get user profile information"""
    query = """SELECT username, firstname, lastname, email, DOB, role, created_at
               FROM Users WHERE username = %s"""
    result = execute_query(query, (username,))
    return result[0] if result else None

def get_mutual_friends(username1, username2):
    """Get mutual friends between two users"""
    query = """SELECT DISTINCT u.username, u.firstname, u.lastname
               FROM Friends f1
               JOIN Friends f2 ON (f1.username_1 = f2.username_1 OR f1.username_1 = f2.username_2 
                                   OR f1.username_2 = f2.username_1 OR f1.username_2 = f2.username_2)
               JOIN Users u ON ((f1.username_1 = u.username OR f1.username_2 = u.username)
                               AND (f2.username_1 = u.username OR f2.username_2 = u.username))
               WHERE ((f1.username_1 = %s OR f1.username_2 = %s) AND f1.status = 'accepted')
                 AND ((f2.username_1 = %s OR f2.username_2 = %s) AND f2.status = 'accepted')
                 AND u.username NOT IN (%s, %s)"""
    return execute_query(query, (username1, username1, username2, username2, username1, username2))

def get_media_by_id(media_id):
    """Get media details by ID"""
    query = """SELECT * FROM Media WHERE media_id = %s"""
    result = execute_query(query, (media_id,))
    return result[0] if result else None

def get_media_full_details(media_id):
    """Get full media details with cast, crew, genres"""
    media = get_media_by_id(media_id)
    if not media:
        return None
    
    genres = execute_query("""SELECT g.name FROM Media_Genres mg
                             JOIN genres g ON mg.genre_id = g.genre_id
                             WHERE mg.media_id = %s""", (media_id,))
    
    cast = execute_query("""SELECT p.name, mc.character_name FROM Media_Cast mc
                           JOIN People p ON mc.person_id = p.person_id
                           WHERE mc.media_id = %s""", (media_id,))
    
    crew = execute_query("""SELECT p.name, mc.role FROM Media_Crew mc
                           JOIN People p ON mc.person_id = p.person_id
                           WHERE mc.media_id = %s""", (media_id,))
    
    media['genres'] = [g['name'] for g in genres] if genres else []
    media['cast'] = cast if cast else []
    media['crew'] = crew if crew else []
    
    return media

def get_episodes_for_series(media_id):
    """Get all episodes for a series"""
    query = """SELECT * FROM Episodes WHERE media_id = %s
               ORDER BY season_number, episode_number"""
    return execute_query(query, (media_id,))

def get_friends(username):
    """Get user's friends"""
    query = """SELECT u.username, u.firstname, u.lastname
               FROM Friends f
               JOIN Users u ON (f.username_1 = u.username OR f.username_2 = u.username)
               WHERE (f.username_1 = %s OR f.username_2 = %s)
               AND f.status = 'accepted'
               AND u.username != %s"""
    return execute_query(query, (username, username, username))

def get_friend_requests(username):
    """Get pending friend requests"""
    query = """SELECT u.username, u.firstname, u.lastname, f.created_at
               FROM Friends f
               JOIN Users u ON f.username_1 = u.username
               WHERE f.username_2 = %s AND f.status = 'pending'"""
    return execute_query(query, (username,))

def send_friend_request(from_user, to_user):
    """Send friend request - validates user exists first"""
    if not user_exists(to_user):
        return None
    query = """INSERT INTO Friends (username_1, username_2, status)
               VALUES (%s, %s, 'pending')
               ON DUPLICATE KEY UPDATE status = 'pending'"""
    return execute_query(query, (from_user, to_user), fetch=False)

def accept_friend_request(username1, username2):
    """Accept friend request"""
    query = """UPDATE Friends SET status = 'accepted'
               WHERE username_1 = %s AND username_2 = %s"""
    return execute_query(query, (username2, username1), fetch=False)

def get_activity_logs(limit=50):
    """Get activity logs for admin"""
    query = """SELECT * FROM Activity_Log ORDER BY changed_at DESC LIMIT %s"""
    return execute_query(query, (limit,))

def get_table_data(table_name):
    """Get all data from a table"""
    query = f"SELECT * FROM {table_name} LIMIT 100"
    return execute_query(query)

def get_table_columns(table_name):
    """Get column names for a table"""
    query = f"DESCRIBE {table_name}"
    return execute_query(query)

def insert_table_record(table_name, data):
    """Insert record into table"""
    columns = ", ".join(data.keys())
    placeholders = ", ".join(["%s"] * len(data))
    query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
    return execute_query(query, tuple(data.values()), fetch=False)

def update_table_record(table_name, id_column, record_id, updates):
    """Update record in table"""
    set_clause = ", ".join([f"{k} = %s" for k in updates.keys()])
    query = f"UPDATE {table_name} SET {set_clause} WHERE {id_column} = %s"
    params = list(updates.values()) + [record_id]
    return execute_query(query, tuple(params), fetch=False)

def delete_table_record(table_name, id_column, record_id):
    """Delete record from table"""
    query = f"DELETE FROM {table_name} WHERE {id_column} = %s"
    return execute_query(query, (record_id,), fetch=False)

def get_user_stats(username):
    """Get user statistics"""
    watchlist_count = execute_query("SELECT COUNT(*) as count FROM playlist WHERE username = %s", (username,))
    series_count = execute_query("""SELECT COUNT(*) as count FROM Series_Progress_Table 
                                    WHERE username = %s""", (username,))
    friends_count = execute_query("""SELECT COUNT(*) as count FROM Friends 
                                     WHERE (username_1 = %s OR username_2 = %s) 
                                     AND status = 'accepted'""", (username, username))
    return {
        'watchlists': watchlist_count[0]['count'] if watchlist_count else 0,
        'series': series_count[0]['count'] if series_count else 0,
        'friends': friends_count[0]['count'] if friends_count else 0
    }

def get_recommendations(username, limit=10):
    """Get media recommendations for user"""
    query = """SELECT DISTINCT m.media_id, m.title, m.poster_image_url, m.average_rating, m.media_type
               FROM Media m
               LEFT JOIN Watchlists_item wi ON m.media_id = wi.media_id AND wi.username = %s
               WHERE wi.media_id IS NULL
               ORDER BY m.average_rating DESC
               LIMIT %s"""
    return execute_query(query, (username, limit))

def set_page(page):
    st.session_state.page = page


def landing_page():
    st.set_page_config(page_title="StreamSync", page_icon="🎥", layout="wide")

    # Header Section
    st.markdown("""
        <div class="header-container">
            <h1 style="font-size: 3.5rem; margin: 0;">🎥 StreamSync</h1>
            <p style="font-size: 1.5rem; margin: 0.5rem 0;">Track. Save. Discover</p>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar Authentication
    with st.sidebar:
        st.markdown("### 🔐 Get Started")
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔑 Login", use_container_width=True, type="primary"):
                set_page('Login')
                st.rerun()
        with col2:
            if st.button("📝 Register", use_container_width=True):
                set_page('Register')
                st.rerun()

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666; font-size: 0.9rem;">
            <p>Join thousands of users tracking their favorite content</p>
        </div>
        """, unsafe_allow_html=True)

    # Features Section
    st.markdown("## ✨ Features")
    st.markdown("---")
    
    # Feature 1
    with st.container():
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            st.markdown("### 📚 Vast Library")
            st.markdown("""
            <div style="padding: 1.5rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; border-left: 5px solid #667eea; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <p style="font-size: 1.2rem; line-height: 1.8; color: #2c3e50; margin: 0;">
                    Explore in the vast library of movies, series, and you name it we have it. 
                    Discover new content from our extensive collection.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            try:
                st.image(image="Resources/vast_library.png", use_container_width=True)
            except:
                st.markdown("![Library](Resources/vast_library.png)")

    st.markdown("---")
    
    # Feature 2
    with st.container():
        col1, col2 = st.columns([1, 1], gap="large")
        with col2:
            st.markdown("### 📋 Custom Playlists")
            st.markdown("""
            <div style="padding: 1.5rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; border-left: 5px solid #764ba2; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <p style="font-size: 1.2rem; line-height: 1.8; color: #2c3e50; margin: 0;">
                    Track your interests with custom playlists. Organize your favorite content 
                    the way you want.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col1:
            try:
                st.image(image="Resources/playlist_tracking.png", use_container_width=True)
            except:
                st.markdown("![Playlist](Resources/playlist_tracking.png)")
    
    st.markdown("---")
    
    # Feature 3
    with st.container():
        col1, col2 = st.columns([1, 1], gap="large")
        with col1:
            st.markdown("### 👥 Social Features")
            st.markdown("""
            <div style="padding: 1.5rem; background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); border-radius: 15px; border-left: 5px solid #f093fb; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                <p style="font-size: 1.2rem; line-height: 1.8; color: #2c3e50; margin: 0;">
                    Make like-minded friends and take suggestions. Share your watchlist 
                    and discover new content together.
                </p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            try:
                st.image(image="Resources/friends.png", use_container_width=True)
            except:
                st.markdown("![Friends](Resources/friends.png)")
    
    st.markdown("---")
    
    # Call to Action
    st.markdown("## 🚀 Ready to Start?")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🎬 Take Me With You", use_container_width=True, type="primary"):
            set_page('Login')
            st.rerun()

def login_page():
    st.set_page_config(page_title="Login - StreamSync", page_icon="🔑", layout="centered")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">🔑 Welcome Back</h1>
                <p style="color: #666; font-size: 1.1rem;">Sign in to continue your journey</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            with st.form("login_form"):
                st.markdown("### Login Details")
                username = st.text_input("👤 Username", placeholder="Enter your username")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("🚀 Log In", use_container_width=True, type="primary"):
                        if username and password:
                            user = authenticate_user(username, password)
                            if user:
                                st.session_state.username = user['username']
                                st.session_state.user_role = user['role']
                                if user['role'] == 'admin':
                                    set_page('Admin')
                                elif user['role'] == 'moderator':
                                    set_page('Database Handler')
                                else:
                                    set_page('User')
                                st.rerun()
                            else:
                                st.error("Invalid username or password")
                        else:
                            st.warning("Please fill in all fields")
                
                with col_btn2:
                    if st.form_submit_button("⬅️ Back", use_container_width=True):
                        set_page('Landing')
                        st.rerun()
        
        if st.button("📝 Go to Register", use_container_width=True):
            set_page('Register')
            st.rerun()

def register_page():
    st.set_page_config(page_title="Register - StreamSync", page_icon="📝", layout="centered")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("""
            <div style="text-align: center; padding: 2rem;">
                <h1 style="font-size: 2.5rem; margin-bottom: 0.5rem;">📝 Get Started</h1>
                <p style="color: #666; font-size: 1.1rem;">Create your account and start tracking</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container(border=True):
            with st.form("register_form"):
                st.markdown("### Personal Information")
                col1, col2 = st.columns(2)
                with col1:
                    first_name = st.text_input("👤 First Name", placeholder="John")
                with col2:
                    last_name = st.text_input("👤 Last Name", placeholder="Doe")

                st.markdown("### Account Details")
                col1, col2 = st.columns(2)
                with col1:
                    username = st.text_input("🔑 Username", placeholder="johndoe")
                with col2:
                    mail_id = st.text_input("📧 Email", placeholder="john@example.com")
                
                dob = st.date_input("📅 Date of Birth", value=None, max_value=datetime.now().date(), min_value=datetime(1900, 1, 1).date())

                st.markdown("### Security")
                col1, col2 = st.columns(2)
                with col1:
                    password = st.text_input("🔒 Password", type="password", placeholder="••••••••")
                with col2:
                    confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="••••••••")
        
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    if st.form_submit_button("✨ Register", use_container_width=True, type="primary"):
                        if username and password and first_name and last_name and mail_id and dob:
                            if password == confirm_password:
                                result = register_user(
                                    username,
                                    first_name,
                                    last_name,
                                    mail_id,
                                    password,
                                    dob,
                                    role='user',
                                    created_by=username
                                )
                                if result:
                                    st.session_state.username = username
                                    st.session_state.user_role = "user"
                                    st.success("Registration successful! 🎉")
                                    set_page('User')
                                    st.rerun()
                                else:
                                    st.error("Registration failed. Username or email may already exist.")
                            else:
                                st.error("Passwords do not match!")
                        else:
                            st.warning("Please fill in all fields")
                
                with col_btn2:
                    if st.form_submit_button("⬅️ Back", use_container_width=True):
                        set_page('Landing')
                        st.rerun()
        
        if st.button("🔑 Already have an account? Login", use_container_width=True):
            set_page('Login')
            st.rerun()



def user_page(username):
    st.set_page_config(page_title="StreamSync - User Dashboard", page_icon="🎥", layout="wide")
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1 style="font-size: 2rem; margin: 0;">🎥 StreamSync</h1>
                <p style="color: #666; margin: 0.5rem 0;">Welcome, {}</p>
            </div>
        """.format(username), unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("### 🧭 Navigation")
        nav_options = {
            "🏠 Home": "Home",
            "🔍 Explore": "Explore",
            "📋 Watchlist": "Watchlist",
            "📺 Series Progress": "Series Progress",
            "👥 Friends": "Friends"
        }
        
        selected = None
        for nav_label, nav_value in nav_options.items():
            if st.button(nav_label, use_container_width=True, 
                        type="primary" if st.session_state.selected_nav == nav_value else "secondary",
                        key=f"nav_{nav_value}"):
                st.session_state.selected_nav = nav_value
                st.rerun()
        
        if st.session_state.selected_nav not in nav_options.values():
            st.session_state.selected_nav = "Home"
        
        selected = st.session_state.selected_nav
        
        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
            st.session_state.selected_nav = "Home"
            set_page('Landing')
            st.rerun()


    if selected == "Home":
        st.markdown(f"# 👋 Welcome, {st.session_state.username}!")
        st.markdown("---")

        stats = get_user_stats(username)
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📋 Watchlists", stats['watchlists'])
        with col2:
            st.metric("📺 Series", stats['series'])
        with col3:
            st.metric("👥 Friends", stats['friends'])

        st.markdown("---")
        
        col1, col2 = st.columns([2, 1], gap="large")
        with col1:
            with st.container(border=True):
                st.markdown("### 💡 Recommendations for You")
                recommendations = get_recommendations(username, 5)
                if recommendations:
                    for rec in recommendations:
                        st.markdown(f"**{rec['title']}** ({rec['media_type']}) - ⭐ {rec['average_rating']}")
                else:
                    st.info("No recommendations available")
        with col2:
            with st.container(border=True):
                st.markdown("### ▶️ Continue Watching")
                progress = get_series_progress(username)
                if progress:
                    for p in progress[:3]:
                        st.markdown(f"**{p['title']}**")
                        if p['episode_title']:
                            st.caption(f"S{p['season_number']}E{p['episode_number']}: {p['episode_title']}")
                else:
                    st.info("No series in progress")

        st.markdown("---")
        
        st.markdown("### 📋 Your Recent Watchlists")
        watchlists = get_user_watchlists(username)
        if watchlists:
            cols = st.columns(min(len(watchlists), 2))
            for i, wl in enumerate(watchlists[:2]):
                with cols[i % 2]:
                    with st.container(border=True):
                        st.markdown(f"#### 📋 {wl['name']}")
                        st.caption(f"{wl['item_count']} items")
        else:
            st.info("No watchlists yet. Create one to get started!")

    elif selected == "Explore":
        if st.session_state.selected_media_id:
            media_details_page(st.session_state.selected_media_id, username)
        else:
            st.markdown("# 🔍 Explore")
            st.markdown("---")
            
            with st.container(border=True):
                st.markdown("### Search Content")
                query = st.text_input("🔎 Search", placeholder="Type to search movies, series, and more...", key="explore_search")
                
                st.markdown("#### Filter Options")
                options = ["All", "Movies", "Series"]
                cols = st.columns(3)
                selected_filters = []
                for col, option in zip(cols, options):
                    with col:
                        if st.checkbox(option, key=f"filter_{option}"):
                            selected_filters.append(option)

            st.markdown("---")
            
            if query or selected_filters:
                results = search_media(query if query else None, selected_filters)
                if results:
                    st.markdown(f"### 📊 Search Results ({len(results)} found)")
                    cols = st.columns(3)
                    for i, media in enumerate(results):
                        with cols[i % 3]:
                            with st.container(border=True):
                                st.markdown(f"**{media['title']}**")
                                st.caption(f"{media['media_type']} • {media['release_year']} • ⭐ {media['average_rating']}")
                                if media['description']:
                                    st.caption(media['description'][:100] + "...")
                                if st.button("View Details", key=f"explore_{media['media_id']}", use_container_width=True):
                                    st.session_state.selected_media_id = media['media_id']
                                    st.rerun()
                else:
                    st.info("No results found")
            else:
                st.info("Enter a search query or select filters to explore content")

    elif selected == "Watchlist":
        if st.session_state.selected_playlist_id:
            watchlist_details_page(st.session_state.selected_playlist_id, username)
        else:
            col1, col2 = st.columns([4, 1], gap="large")
            with col1:
                st.markdown("# 📋 Your Watchlists")
            with col2:
                st.write("")
                if st.button("➕ Create New", use_container_width=True, type="primary"):
                    set_page('Create Watchlist')
                    st.rerun()

            st.markdown("---")

            watchlists = get_user_watchlists(username)
            if watchlists:
                cols = st.columns(2)
                for i, wl in enumerate(watchlists):
                    with cols[i % 2]:
                        with st.container(border=True):
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"#### 📋 {wl['name']}")
                                st.caption(f"Created: {wl['created_at']} • {wl['item_count']} items")
                            with col2:
                                if st.button("🗑️", key=f"delete_wl_{i}", help="Delete watchlist"):
                                    if delete_watchlist(wl['playlist_id'], deleted_by=username):
                                        st.success("Watchlist deleted!")
                                        st.rerun()
                            if st.button("View Details", key=f"watchlist_{i}", use_container_width=True):
                                st.session_state.selected_playlist_id = wl['playlist_id']
                                st.rerun()
            else:
                st.info("No watchlists yet. Create one to get started!")

    elif selected == "Series Progress":
        if st.session_state.selected_media_id and st.session_state.get('update_series_mode'):
            media_details_page(st.session_state.selected_media_id, username)
        else:
            col1, col2 = st.columns([4, 1], gap="large")
            with col1:
                st.markdown("# 📺 Your Series Progress")
            with col2:
                st.write("")
                if st.button("➕ Add Series", use_container_width=True, type="primary"):
                    set_page('Add Series')
                    st.rerun()

            st.markdown("---")

            progress_list = get_series_progress(username)
            if progress_list:
                cols = st.columns(2)
                for i, series in enumerate(progress_list):
                    with cols[i % 2]:
                        with st.container(border=True):
                            st.markdown(f"#### 📺 {series['title']}")
                            if series['episode_title']:
                                st.markdown(f"**Progress:** Season {series['season_number']}, Episode {series['episode_number']}")
                                st.caption(f"{series['episode_title']}")
                            else:
                                st.caption("Not started")
                            st.caption(f"Last watched: {series['last_watched_at']}")
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.button("Update Progress", key=f"series_{i}", use_container_width=True):
                                    st.session_state.selected_media_id = series['media_id']
                                    st.session_state.update_series_mode = True
                                    st.rerun()
                            with col2:
                                if st.button("🗑️ Remove", key=f"remove_series_{i}", use_container_width=True):
                                    if remove_series_progress(username, series['media_id'], removed_by=username):
                                        st.success("Removed from progress!")
                                        st.rerun()
            else:
                st.info("No series in progress. Add a series to track your progress!")

    elif selected == "Friends":
        if st.session_state.selected_friend:
            friend_profile_page(st.session_state.selected_friend, username)
        else:
            col1, col2 = st.columns([4, 1], gap="large")
            with col1:
                st.markdown("# 👥 Friends")
            with col2:
                st.write("")
                if st.button("📬 Requests", use_container_width=True, type="primary"):
                    set_page("Friend Requests")
                    st.rerun()

            st.markdown("---")

            col1, col2 = st.columns(2, gap="large")
            with col1:
                with st.container(border=True):
                    st.markdown("### 👫 Your Friends")
                    friends = get_friends(username)
                    if friends:
                        for friend in friends:
                            if st.button(f"👤 {friend['firstname']} {friend['lastname']} (@{friend['username']})", 
                                       key=f"friend_{friend['username']}", use_container_width=True):
                                st.session_state.selected_friend = friend['username']
                                st.rerun()
                    else:
                        st.info("No friends yet")
            with col2:
                with st.container(border=True):
                    st.markdown("### 🔍 Find Friends")
                    search_query = st.text_input("Search users", placeholder="Enter username or name...", key="friend_search")
                    if st.button("🔍 Search & Send Request", use_container_width=True):
                        if search_query and search_query != username:
                            if user_exists(search_query):
                                if send_friend_request(username, search_query):
                                    st.success(f"Friend request sent to {search_query}!")
                                else:
                                    st.error("Failed to send request. You may already be friends or have a pending request.")
                            else:
                                st.error("User not found. Please check the username.")
                        else:
                            st.warning("Enter a valid username")
                    
                    st.markdown("---")
                    st.markdown("### 👥 Suggested Users")
                    all_users = execute_query("SELECT username, firstname, lastname FROM Users WHERE username != %s LIMIT 10", (username,))
                    if all_users:
                        for user in all_users[:5]:
                            is_friend = any(f['username'] == user['username'] for f in (friends or []))
                            if not is_friend:
                                mutual = get_mutual_friends(username, user['username'])
                                mutual_text = f" ({len(mutual)} mutual)" if mutual else ""
                                if st.button(f"➕ {user['firstname']} {user['lastname']}{mutual_text}", 
                                           key=f"suggest_{user['username']}", use_container_width=True):
                                    if send_friend_request(username, user['username']):
                                        st.success(f"Request sent to {user['username']}!")
                                        st.rerun()

def media_details_page(media_id, username):
    """Display detailed media information"""
    st.markdown("# 🎬 Media Details")
    
    if st.button("⬅️ Back to Explore", use_container_width=True):
        st.session_state.selected_media_id = None
        st.rerun()
    
    st.markdown("---")
    
    media = get_media_full_details(media_id)
    if not media:
        st.error("Media not found")
        return
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        if media.get('poster_image_url'):
            st.image(media['poster_image_url'], use_container_width=True)
        else:
            st.info("No poster available")
    
    with col2:
        st.markdown(f"# {media['title']}")
        st.markdown(f"**Type:** {media['media_type']} | **Year:** {media['release_year']} | **Rating:** ⭐ {media['average_rating']}")
        st.markdown(f"**Age Rating:** {media['age_rating']}")
        
        if media.get('genres'):
            genres_str = ", ".join(media['genres'])
            st.markdown(f"**Genres:** {genres_str}")
        
        st.markdown("---")
        st.markdown("### Description")
        st.markdown(media['description'] or "No description available")
    
    st.markdown("---")
    
    if media.get('cast'):
        st.markdown("### 🎭 Cast")
        cols = st.columns(min(len(media['cast']), 4))
        for i, actor in enumerate(media['cast']):
            with cols[i % 4]:
                with st.container(border=True):
                    st.markdown(f"**{actor['name']}**")
                    if actor.get('character_name'):
                        st.caption(f"as {actor['character_name']}")
    
    if media.get('crew'):
        st.markdown("### 👥 Crew")
        cols = st.columns(min(len(media['crew']), 4))
        for i, member in enumerate(media['crew']):
            with cols[i % 4]:
                with st.container(border=True):
                    st.markdown(f"**{member['name']}**")
                    st.caption(f"{member['role']}")
    
    if media['media_type'] == 'Series':
        st.markdown("---")
        st.markdown("### 📺 Episodes")
        episodes = get_episodes_for_series(media_id)
        if episodes:
            if st.session_state.get('update_series_mode'):
                st.info("Select an episode to update your progress")
                for ep in episodes:
                    if st.button(f"S{ep['season_number']}E{ep['episode_number']}: {ep['title']}", 
                                key=f"ep_{ep['episode_id']}", use_container_width=True):
                        if update_series_progress(username, media_id, ep['episode_id']):
                            st.success(f"Progress updated to {ep['title']}!")
                            st.session_state.update_series_mode = False
                            st.rerun()
            else:
                for ep in episodes[:10]:
                    st.markdown(f"**S{ep['season_number']}E{ep['episode_number']}:** {ep['title']}")
                    st.caption(f"Aired: {ep['air_date']}")
        else:
            st.info("No episodes available")

def add_series_page(username):
    st.set_page_config(page_title="Add Series - StreamSync", page_icon="📺", layout="wide")
    
    col1, col2 = st.columns([4, 1], gap="large")
    with col1:
        st.markdown("# ➕ Add Series")
    with col2:
        st.write("")
        if st.button("⬅️ Go Back", use_container_width=True):
            set_page('User')
            st.rerun()

    st.markdown("---")

    with st.container(border=True):
        st.markdown("### 🔍 Search for Series")
        query = st.text_input("🔎 Search Series", placeholder="Type to search for series...", key="add_series_search")
        
        st.markdown("#### Filter Options")
        options = ["All", "Series", "Genre"]
        cols = st.columns(3)
        selected_filters = ["Series"]
        for col, option in zip(cols, options):
            with col:
                if st.checkbox(option, key=f"add_{option}", value=(option == "Series")):
                    if option not in selected_filters:
                        selected_filters.append(option)
                    if option == "All":
                        selected_filters = ["Series"]

    st.markdown("---")
    
    if query:
        results = search_media(query, selected_filters)
        if results:
            st.markdown(f"### 📊 Search Results ({len(results)} found)")
            for media in results:
                with st.container(border=True):
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{media['title']}** ({media['release_year']})")
                        st.caption(f"⭐ {media['average_rating']}")
                        if media['description']:
                            st.caption(media['description'][:200] + "...")
                    with col2:
                        if st.button("Add to Progress", key=f"add_{media['media_id']}", use_container_width=True):
                            episodes = get_episodes_for_series(media['media_id'])
                            if episodes:
                                if update_series_progress(username, media['media_id'], episodes[0]['episode_id']):
                                    st.success(f"Added {media['title']} to your series progress!")
                                    st.rerun()
                            else:
                                st.warning("No episodes found for this series")
        else:
            st.info("No series found")
    else:
        st.info("Enter a search query to find series")

def watchlist_details_page(playlist_id, username):
    """Display watchlist details with items"""
    st.markdown("# 📋 Watchlist Details")
    
    col1, col2 = st.columns([4, 1])
    with col1:
        if st.button("⬅️ Back to Watchlists", use_container_width=True):
            st.session_state.selected_playlist_id = None
            st.session_state.add_to_watchlist_mode = False
            st.rerun()
    with col2:
        if st.button("➕ Add Media", use_container_width=True, type="primary"):
            st.session_state.add_to_watchlist_mode = True
            st.session_state.add_to_watchlist_id = playlist_id
            st.rerun()
    
    st.markdown("---")
    
    items = get_watchlist_items(playlist_id) or []
    playlist_info = execute_query("SELECT name, created_at FROM playlist WHERE playlist_id = %s", (playlist_id,))
    playlist_meta = playlist_info[0] if playlist_info else None
    
    if playlist_meta:
        st.markdown(f"### {playlist_meta.get('name') or 'Untitled Playlist'}")
        st.caption(f"Created: {playlist_meta.get('created_at')} • {len(items)} items")
    else:
        st.warning("Playlist not found.")
    
    st.markdown("---")
    
    if st.session_state.get('add_to_watchlist_mode') and st.session_state.get('add_to_watchlist_id') == playlist_id:
        st.markdown("### 🔍 Search and Add Media")
        search_query = st.text_input("Search movies or series", key="add_watchlist_search")
        if search_query:
            results = search_media(search_query)
            if results:
                for media in results[:5]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"**{media['title']}** ({media['media_type']})")
                    with col2:
                        if st.button("➕ Add", key=f"add_{playlist_id}_{media['media_id']}", use_container_width=True):
                            if add_to_watchlist(playlist_id, media['media_id'], added_by=st.session_state.get('username')):
                                st.success(f"Added {media['title']} to watchlist!")
                                st.session_state.add_to_watchlist_mode = False
                                st.rerun()
        if st.button("Cancel", key="cancel_add_watchlist"):
            st.session_state.add_to_watchlist_mode = False
            st.rerun()
        st.markdown("---")
    
    if items:
        for item in items:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    media = get_media_by_id(item['media_id'])
                    if media:
                        st.markdown(f"**{media['title']}** ({media['media_type']})")
                        st.caption(f"⭐ {media['average_rating']} • {media['release_year']}")
                        if media.get('description'):
                            st.caption(media['description'][:150] + "...")
                with col2:
                    if st.button("View Details", key=f"view_{item['playlist_id']}_{item['media_id']}", use_container_width=True):
                        st.session_state.selected_media_id = item['media_id']
                        st.session_state.update_series_mode = False
                        st.rerun()
                with col3:
                    if st.button("🗑️ Remove", key=f"remove_{item['playlist_id']}_{item['media_id']}", use_container_width=True):
                        if remove_from_watchlist(item['playlist_id'], item['media_id'], removed_by=st.session_state.get('username')):
                            st.success("Removed from watchlist!")
                            st.rerun()
    else:
        st.info("This watchlist is empty")

def friend_profile_page(friend_username, current_username):
    """Display friend profile in read-only mode"""
    st.markdown("# 👤 Friend Profile")
    
    if st.button("⬅️ Back to Friends", use_container_width=True):
        st.session_state.selected_friend = None
        st.rerun()
    
    st.markdown("---")
    
    profile = get_user_profile(friend_username)
    if not profile:
        st.error("User not found")
        return
    
    col1, col2 = st.columns([1, 2], gap="large")
    with col1:
        st.markdown("### Profile Information")
        with st.container(border=True):
            st.markdown(f"**Username:** {profile['username']}")
            st.markdown(f"**Name:** {profile['firstname']} {profile['lastname']}")
            st.markdown(f"**Email:** {profile['email']}")
            if profile.get('DOB'):
                st.markdown(f"**Date of Birth:** {profile['DOB']}")
            st.markdown(f"**Role:** {profile['role']}")
            if profile.get('created_at'):
                st.caption(f"Member since: {profile['created_at']}")
    
    with col2:
        st.markdown("### Activity")
        with st.container(border=True):
            stats = get_user_stats(friend_username)
            st.metric("Watchlists", stats['watchlists'])
            st.metric("Series in Progress", stats['series'])
            st.metric("Friends", stats['friends'])
    
    mutual = get_mutual_friends(current_username, friend_username)
    if mutual:
        st.markdown("---")
        st.markdown(f"### 👥 Mutual Friends ({len(mutual)})")
        cols = st.columns(min(len(mutual), 4))
        for i, friend in enumerate(mutual):
            with cols[i % 4]:
                with st.container(border=True):
                    st.markdown(f"**{friend['firstname']} {friend['lastname']}**")
                    st.caption(f"@{friend['username']}")

def create_watchlist_page(username):
    st.set_page_config(page_title="Create Watchlist - StreamSync", page_icon="📋", layout="centered")
    
    col1, col2 = st.columns([4, 1], gap="large")
    with col1:
        st.markdown("# ➕ Create New Watchlist")
    with col2:
        st.write("")
        if st.button("⬅️ Go Back", use_container_width=True):
            set_page('User')
            st.rerun()

    st.markdown("---")

    with st.container(border=True):
        with st.form("create_watchlist_form"):
            st.markdown("### Watchlist Details")
            watchlist_name = st.text_input("📋 Watchlist Name", placeholder="Enter watchlist name...")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("✨ Create Watchlist", use_container_width=True, type="primary"):
                    if watchlist_name:
                        if create_watchlist(username, watchlist_name):
                            st.success(f"Watchlist '{watchlist_name}' created successfully! 🎉")
                            set_page('User')
                            st.rerun()
                        else:
                            st.error("Failed to create watchlist")
                    else:
                        st.warning("Please enter a watchlist name")
            with col2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    set_page('User')
                    st.rerun()

def friend_requests(username):
    st.set_page_config(page_title="Friend Requests - StreamSync", page_icon="📬", layout="wide")
    
    col1, col2 = st.columns([4, 1], gap="large")
    with col1:
        st.markdown("# 📬 Friend Requests")
    with col2:
        st.write("")
        if st.button("⬅️ Go Back", use_container_width=True):
            set_page('User')
            st.rerun()

    st.markdown("---")

    requests = get_friend_requests(username)
    if requests:
        for req in requests:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.markdown(f"**{req['firstname']} {req['lastname']}** (@{req['username']})")
                    st.caption(f"Sent: {req['created_at']}")
                with col2:
                    if st.button("✅ Accept", key=f"accept_{req['username']}", use_container_width=True):
                        if accept_friend_request(username, req['username']):
                            st.success("Friend request accepted!")
                            st.rerun()
                with col3:
                    if st.button("❌ Decline", key=f"decline_{req['username']}", use_container_width=True):
                        st.info("Decline functionality can be added")
    else:
        st.info("No pending friend requests")


def admin_page():
    st.set_page_config(page_title="StreamSync - Admin Dashboard", page_icon="🎛️", layout="wide")
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1 style="font-size: 2rem; margin: 0;">🎛️ Admin</h1>
                <p style="color: #666; margin: 0.5rem 0;">Dashboard</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("### 🧭 Navigation")
        nav_options = {
            "🏠 Home": "Home",
            "🔄 Changes": "Changes",
            "👥 Database Handlers": "Database Handlers"
        }
        
        selected = None
        for nav_label, nav_value in nav_options.items():
            if st.button(nav_label, use_container_width=True, 
                        type="primary" if st.session_state.get('admin_nav', 'Home') == nav_value else "secondary",
                        key=f"admin_nav_{nav_value}"):
                st.session_state.admin_nav = nav_value
                st.rerun()
        
        if 'admin_nav' not in st.session_state or st.session_state.admin_nav not in nav_options.values():
            st.session_state.admin_nav = "Home"
        
        selected = st.session_state.admin_nav
        
        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
            st.session_state.admin_nav = "Home"
            set_page('Landing')
            st.rerun()

    if selected != "Database Handlers":
        st.session_state.selected_handler_user = None

    if selected == "Home":
        st.markdown("# 🎛️ Admin Dashboard")
        st.markdown("Welcome to the Admin Dashboard! Monitor system performance and manage key operations.")
        st.markdown("---")

        st.markdown("### 📊 System Metrics")
        user_count = execute_query("SELECT COUNT(*) as count FROM Users", ())
        media_count = execute_query("SELECT COUNT(*) as count FROM Media", ())
        handlers_count = execute_query("SELECT COUNT(*) as count FROM Users WHERE role = 'moderator'", ())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.metric(label="Total Users", value=user_count[0]['count'] if user_count else 0)
        with col2:
            with st.container(border=True):
                st.metric(label="Total Media", value=media_count[0]['count'] if media_count else 0)
        with col3:
            with st.container(border=True):
                st.metric(label="Database Handlers", value=handlers_count[0]['count'] if handlers_count else 0)

        st.markdown("---")
        st.info("💡 Monitor system metrics and manage database operations efficiently.")

    elif selected == "Changes":
        st.markdown("# 🔄 Changes")
        st.markdown("Track all recent database changes and operations performed by handlers.")
        st.markdown("---")

        table_filter = st.selectbox("Filter by Table", ["All Tables", "Users", "Media", "genres", "Episodes", 
                                                         "Watchlists_item", "playlist", "Playlist_item", 
                                                         "Media_Genres", "Series_Progress_Table", "Reviews_Table", 
                                                         "Friends", "People", "Media_Cast", "Media_Crew", "Activity_Log"])
        
        if table_filter == "All Tables":
            logs = get_activity_logs(100)
        else:
            logs = execute_query("SELECT * FROM Activity_Log WHERE table_name = %s ORDER BY changed_at DESC LIMIT 100", (table_filter,))
        
        if logs:
            df = pd.DataFrame(logs)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No activity logs available")

        st.markdown("---")
        st.success("✅ All changes are logged and monitored for audit purposes.")

    elif selected == "Database Handlers":
        col1, col2 = st.columns([4, 1], gap="large")
        with col1:
            st.markdown("# 👥 Database Handlers")
        with col2:
            st.write("")
            if st.button("➕ Add Handler", use_container_width=True, type="primary"):
                set_page('Add Handler')
                st.rerun()

        st.markdown("Manage and view all active database handlers.")
        st.markdown("---")

        handlers = execute_query(
            "SELECT username, firstname, lastname, email, role, created_at FROM Users WHERE role IN ('moderator', 'admin')",
            ()
        ) or []

        if st.session_state.selected_handler_user:
            profile = get_user_profile(st.session_state.selected_handler_user)
            if profile:
                stats = get_user_stats(profile['username'])
                with st.container(border=True):
                    col_a, col_b = st.columns([2, 1], gap="large")
                    with col_a:
                        st.markdown(f"### 👤 {profile['firstname']} {profile['lastname']} (@{profile['username']})")
                        st.markdown(f"**Role:** {profile['role']}")
                        st.markdown(f"**Email:** {profile['email']}")
                        if profile.get('DOB'):
                            st.markdown(f"**DOB:** {profile['DOB']}")
                        if profile.get('created_at'):
                            st.caption(f"Joined on {profile['created_at']}")
                    with col_b:
                        st.markdown("### 📊 Stats")
                        st.metric("Watchlists", stats['watchlists'])
                        st.metric("Series", stats['series'])
                        st.metric("Friends", stats['friends'])
                if st.button("⬅️ Back to Handlers", use_container_width=True):
                    st.session_state.selected_handler_user = None
                    st.rerun()
            else:
                st.warning("Handler not found.")
                st.session_state.selected_handler_user = None
        else:
            if handlers:
                cols = st.columns(2)
                for i, handler in enumerate(handlers):
                    with cols[i % 2]:
                        with st.container(border=True):
                            st.markdown(f"#### 👤 {handler['firstname']} {handler['lastname']} (@{handler['username']})")
                            st.caption(f"Role: {handler['role']} • Member since {handler.get('created_at')}")
                            if st.button("View Details", key=f"admin_handler_{handler['username']}", use_container_width=True):
                                st.session_state.selected_handler_user = handler['username']
                                st.rerun()
            else:
                st.info("No database handlers assigned yet.")

        st.markdown("---")
        st.info("💡 Handlers ensure data integrity and perform maintenance tasks.")

def database_handler_page():
    st.set_page_config(page_title="StreamSync - Database Handler", page_icon="🗄️", layout="wide")
    
    # Sidebar Navigation
    with st.sidebar:
        st.markdown("""
            <div style="text-align: center; padding: 1rem;">
                <h1 style="font-size: 2rem; margin: 0;">🗄️ Database</h1>
                <p style="color: #666; margin: 0.5rem 0;">Handler Dashboard</p>
            </div>
        """, unsafe_allow_html=True)
        st.markdown("---")
        
        st.markdown("### 🧭 Navigation")
        nav_options = {
            "🏠 Home": "Home",
            "🔄 Changes": "Changes",
            "🗃️ Database": "Database",
            "👥 Database Handlers": "Database Handlers"
        }
        
        selected = None
        for nav_label, nav_value in nav_options.items():
            if st.button(nav_label, use_container_width=True, 
                        type="primary" if st.session_state.get('db_nav', 'Home') == nav_value else "secondary",
                        key=f"db_nav_{nav_value}"):
                st.session_state.db_nav = nav_value
                st.rerun()
        
        if 'db_nav' not in st.session_state or st.session_state.db_nav not in nav_options.values():
            st.session_state.db_nav = "Home"
        
        selected = st.session_state.db_nav
        
        st.markdown("---")
        if st.button("🚪 Log Out", use_container_width=True, type="secondary"):
            st.session_state.db_nav = "Home"
            set_page('Landing')
            st.rerun()

    if selected != "Database Handlers":
        st.session_state.selected_handler_user = None

    if selected == "Home":
        st.markdown("# 🗄️ Database Handler Dashboard")
        st.markdown("Manage and monitor database operations efficiently.")
        st.markdown("---")

        st.markdown("### 📈 Database Metrics")
        user_count = execute_query("SELECT COUNT(*) as count FROM Users", ())
        media_count = execute_query("SELECT COUNT(*) as count FROM Media", ())
        recent_changes = execute_query("SELECT COUNT(*) as count FROM Activity_Log WHERE changed_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)", ())
        
        col1, col2, col3 = st.columns(3)
        with col1:
            with st.container(border=True):
                st.metric(label="Total Users", value=user_count[0]['count'] if user_count else 0)
        with col2:
            with st.container(border=True):
                st.metric(label="Total Media", value=media_count[0]['count'] if media_count else 0)
        with col3:
            with st.container(border=True):
                st.metric(label="Changes (7 days)", value=recent_changes[0]['count'] if recent_changes else 0)

        st.markdown("---")
        
        st.markdown("### 🚀 Quick Actions")
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("➕ Add New User", use_container_width=True, type="primary"):
                st.session_state.db_add_user = True
                st.rerun()
        with col2:
            if st.button("🗃️ View Tables", use_container_width=True):
                st.session_state.db_nav = "Database"
                st.rerun()
        with col3:
            if st.button("🔄 View Changes", use_container_width=True):
                st.session_state.db_nav = "Changes"
                st.rerun()

        if st.session_state.get('db_add_user'):
            st.markdown("---")
            with st.container(border=True):
                st.markdown("### ➕ Add New User")
                with st.form("add_user_form"):
                    col1, col2 = st.columns(2)
                    with col1:
                        username = st.text_input("👤 Username", key="db_username")
                        firstname = st.text_input("👤 First Name", key="db_firstname")
                        email = st.text_input("📧 Email", key="db_email")
                    with col2:
                        lastname = st.text_input("👤 Last Name", key="db_lastname")
                        dob = st.date_input("📅 Date of Birth", value=None, max_value=datetime.now().date(), min_value=datetime(1900, 1, 1).date(), key="db_dob")
                        role = st.selectbox("💼 Role", ["user", "moderator", "admin"], key="db_role")
                    
                    password = st.text_input("🔒 Password", type="password", key="db_password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("✨ Create User", use_container_width=True, type="primary"):
                            if username and password and firstname and lastname and email:
                                if register_user(
                                    username,
                                    firstname,
                                    lastname,
                                    email,
                                    password,
                                    dob,
                                    role=role,
                                    created_by=st.session_state.get('username')
                                ):
                                    st.success(f"User '{username}' created successfully!")
                                    st.session_state.db_add_user = False
                                    st.rerun()
                                else:
                                    st.error("Failed to create user. Username may already exist.")
                            else:
                                st.warning("Please fill in all required fields")
                    with col2:
                        if st.form_submit_button("❌ Cancel", use_container_width=True):
                            st.session_state.db_add_user = False
                            st.rerun()

        st.markdown("---")
        st.info("💡 Use quick actions to efficiently manage database operations.")

    elif selected == "Changes":
        st.markdown("# 🔄 Changes")
        st.markdown("Track all recent database changes and operations performed by handlers.")
        st.markdown("---")

        table_filter = st.selectbox("Filter by Table", ["All Tables", "Users", "Media", "genres", "Episodes", 
                                                         "Watchlists_item", "playlist", "Playlist_item", 
                                                         "Media_Genres", "Series_Progress_Table", "Reviews_Table", 
                                                         "Friends", "People", "Media_Cast", "Media_Crew", "Activity_Log"])
        
        if table_filter == "All Tables":
            logs = get_activity_logs(100)
        else:
            logs = execute_query("SELECT * FROM Activity_Log WHERE table_name = %s ORDER BY changed_at DESC LIMIT 100", (table_filter,))
        
        if logs:
            df = pd.DataFrame(logs)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info("No activity logs available")

        st.markdown("---")
        st.success("✅ All changes are logged and monitored for audit purposes.")

    elif selected == "Database":
        st.markdown("# 🗃️ Database")
        st.markdown("Access and manage all database tables.")
        st.markdown("---")

        st.markdown("### Available Tables")
        tables = ["Users", "Media", "genres", "Episodes", "Watchlists_item", "playlist", "Playlist_item", 
                  "Media_Genres", "Series_Progress_Table", "Reviews_Table", "Friends", "People", 
                  "Media_Cast", "Media_Crew", "Activity_Log"]

        cols = st.columns(3)
        for i, table in enumerate(tables):
            with cols[i % 3]:
                if st.button(f"📋 {table}", use_container_width=True, key=f"table_{i}"):
                    st.session_state.selected_table = table
                    set_page('Table Data')
                    st.rerun()

        st.markdown("---")
        st.info("💡 Click on a table to view and edit its data.")

    elif selected == "Database Handlers":
        st.markdown("# 👥 Database Handlers")
        st.markdown("Manage and view all active database handlers.")
        st.markdown("---")

        handlers = execute_query(
            "SELECT username, firstname, lastname, email, role, created_at FROM Users WHERE role IN ('moderator', 'admin')",
            ()
        ) or []

        if st.session_state.selected_handler_user:
            profile = get_user_profile(st.session_state.selected_handler_user)
            if profile:
                stats = get_user_stats(profile['username'])
                with st.container(border=True):
                    col1, col2 = st.columns([2, 1], gap="large")
                    with col1:
                        st.markdown(f"### 👤 {profile['firstname']} {profile['lastname']} (@{profile['username']})")
                        st.markdown(f"**Role:** {profile['role']}")
                        st.markdown(f"**Email:** {profile['email']}")
                        if profile.get('DOB'):
                            st.markdown(f"**DOB:** {profile['DOB']}")
                        if profile.get('created_at'):
                            st.caption(f"Joined on {profile['created_at']}")
                    with col2:
                        st.markdown("### 📊 Stats")
                        st.metric("Watchlists", stats['watchlists'])
                        st.metric("Series", stats['series'])
                        st.metric("Friends", stats['friends'])
                if st.button("⬅️ Back to Handlers", use_container_width=True):
                    st.session_state.selected_handler_user = None
                    st.rerun()
            else:
                st.warning("Handler not found.")
                st.session_state.selected_handler_user = None
        else:
            if handlers:
                cols = st.columns(2)
                for i, handler in enumerate(handlers):
                    with cols[i % 2]:
                        with st.container(border=True):
                            st.markdown(f"#### 👤 {handler['firstname']} {handler['lastname']} (@{handler['username']})")
                            st.caption(f"Role: {handler['role']} • Member since {handler.get('created_at')}")
                            if st.button("View Details", key=f"db_handler_{handler['username']}", use_container_width=True):
                                st.session_state.selected_handler_user = handler['username']
                                st.rerun()
            else:
                st.info("No database handlers assigned yet.")

        st.markdown("---")
        st.info("💡 Handlers ensure data integrity and perform maintenance tasks.")

def table_data_page():
    st.set_page_config(page_title="Table Data - StreamSync", page_icon="📊", layout="wide")
    
    table_name = st.session_state.get('selected_table', 'Users')
    
    col1, col2 = st.columns([4, 1], gap="large")
    with col1:
        st.markdown(f"# 📊 Data in {table_name}")
    with col2:
        st.write("")
        if st.button("⬅️ Go Back", use_container_width=True):
            set_page('Database Handler')
            st.rerun()

    st.markdown("---")

    data = get_table_data(table_name) or []
    if data:
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("No data available or table doesn't exist")

    st.markdown("---")
    
    columns = get_table_columns(table_name)
    if not columns:
        st.warning("Unable to load table metadata.")
        return

    def detect_id_column(cols):
        primary = next((c['Field'] for c in cols if c.get('Key') == 'PRI'), None)
        if primary:
            return primary
        fallback = next(
            (
                c['Field'] for c in cols
                if c['Field'].lower().endswith('_id') or c['Field'].lower() == 'id'
            ),
            None
        )
        return fallback or cols[0]['Field']

    id_col = detect_id_column(columns)
    editable_columns = [
        col for col in columns
        if col['Field'] not in ['created_at', 'updated_at', 'changed_at'] and col['Extra'] != 'auto_increment'
    ]

    tab1, tab2, tab3 = st.tabs(["➕ Insert New Record", "✏️ Update Existing Record", "🗑️ Delete Record"])
    
    with tab1:
        with st.container(border=True):
            st.markdown("### ➕ Insert New Record")
            with st.form(f"insert_{table_name}"):
                form_data = {}
                for col in editable_columns:
                    form_data[col['Field']] = st.text_input(col['Field'], key=f"insert_{table_name}_{col['Field']}")
                
                if st.form_submit_button("✨ Insert", use_container_width=True, type="primary"):
                    filtered_data = {k: v for k, v in form_data.items() if v}
                    if filtered_data:
                        if insert_table_record(table_name, filtered_data):
                            record_identifier = filtered_data.get(id_col, 'N/A')
                            log_activity(
                                table_name,
                                "INSERT",
                                record_identifier,
                                f"Inserted record into {table_name}: {filtered_data}",
                                st.session_state.get('username')
                            )
                            st.success("Record inserted successfully! 🎉")
                            st.rerun()
                        else:
                            st.error("Failed to insert record")
                    else:
                        st.warning("Please fill in at least one field")
    
    with tab2:
        with st.container(border=True):
            st.markdown("### ✏️ Update Existing Record")
            if not data:
                st.info("No data available to update")
            else:
                record_options = {}
                for record in data:
                    record_id_value = record.get(id_col)
                    if record_id_value is None:
                        continue
                    display_val = str(record_id_value)
                    if len(display_val) > 60:
                        display_val = display_val[:60] + "..."
                    display_key = f"{id_col}: {display_val}"
                    if display_key not in record_options:
                        record_options[display_key] = record

                if not record_options:
                    st.warning("Could not determine records for updating.")
                else:
                    selected_label = st.selectbox("Select record to update", list(record_options.keys()), key=f"select_update_{table_name}")
                    selected_record = record_options[selected_label]
                    record_id_value = selected_record.get(id_col)

                    with st.form(f"update_{table_name}"):
                        st.markdown(f"**Updating record with {id_col} = {record_id_value}**")
                        update_inputs = {}
                        for col in editable_columns:
                            if col['Field'] == id_col:
                                continue
                            current_val = selected_record.get(col['Field'], '')
                            if current_val is None:
                                current_val = ''
                            update_inputs[col['Field']] = st.text_input(
                                col['Field'],
                                value=str(current_val),
                                key=f"update_{table_name}_{col['Field']}_{record_id_value}"
                            )

                        if st.form_submit_button("💾 Update Record", use_container_width=True, type="primary"):
                            changes = {
                                field: value for field, value in update_inputs.items()
                                if str(selected_record.get(field, '')) != value and value != ''
                            }
                            if changes:
                                if update_table_record(table_name, id_col, record_id_value, changes):
                                    log_activity(
                                        table_name,
                                        "UPDATE",
                                        record_id_value,
                                        f"Updated fields {list(changes.keys())} in {table_name}",
                                        st.session_state.get('username')
                                    )
                                    st.success("Record updated successfully! 🎉")
                                    st.rerun()
                                else:
                                    st.error("Failed to update record")
                            else:
                                st.warning("No changes detected. Please modify at least one field.")

    with tab3:
        with st.container(border=True):
            st.markdown("### 🗑️ Delete Record")
            if not data:
                st.info("No data available to delete")
            else:
                delete_options = {}
                for record in data:
                    record_id_value = record.get(id_col)
                    if record_id_value is None:
                        continue
                    display_val = str(record_id_value)
                    if len(display_val) > 60:
                        display_val = display_val[:60] + "..."
                    display_key = f"{id_col}: {display_val}"
                    if display_key not in delete_options:
                        delete_options[display_key] = record_id_value

                if not delete_options:
                    st.warning("Could not determine records for deletion.")
                else:
                    col_select, col_button = st.columns([3, 1])
                    with col_select:
                        selected_delete_label = st.selectbox(
                            "Select record to delete",
                            list(delete_options.keys()),
                            key=f"select_delete_{table_name}"
                        )
                    with col_button:
                        if st.button("🗑️ Delete", use_container_width=True, type="primary"):
                            record_id_value = delete_options[selected_delete_label]
                            if delete_table_record(table_name, id_col, record_id_value):
                                log_activity(
                                    table_name,
                                    "DELETE",
                                    record_id_value,
                                    f"Deleted record from {table_name}",
                                    st.session_state.get('username')
                                )
                                st.success("Record deleted successfully!")
                                st.rerun()
                            else:
                                st.error("Failed to delete record")

def add_handler_page():
    st.set_page_config(page_title="Add Handler - StreamSync", page_icon="➕", layout="centered")
    
    col1, col2 = st.columns([4, 1], gap="large")
    with col1:
        st.markdown("# ➕ Add New Handler")
    with col2:
        st.write("")
        if st.button("⬅️ Go Back", use_container_width=True):
            set_page('Admin')
            st.rerun()

    st.markdown("---")

    with st.container(border=True):
        with st.form("add_handler_form"):
            st.markdown("### Handler Information")
            username = st.text_input("👤 Username", placeholder="Enter username...")
            promotion_role = st.selectbox("💼 Assign Role", ["moderator", "admin"])
            
            col_btn1, col_btn2 = st.columns([1, 1])
            with col_btn1:
                if st.form_submit_button("✨ Add Handler", use_container_width=True, type="primary"):
                    if username:
                        if user_exists(username):
                            query = "UPDATE Users SET role = %s WHERE username = %s"
                            if execute_query(query, (promotion_role, username), fetch=False):
                                log_activity(
                                    "Users",
                                    "UPDATE",
                                    username,
                                    f"Promoted to {promotion_role}",
                                    st.session_state.get('username')
                                )
                                st.success(f"Handler '{username}' added successfully! 🎉")
                                st.session_state.selected_handler_user = username
                                set_page('Admin')
                                st.rerun()
                            else:
                                st.error("Failed to add handler")
                        else:
                            st.error("User does not exist. Please enter a valid username.")
                    else:
                        st.warning("Please enter a username")
            with col_btn2:
                if st.form_submit_button("❌ Cancel", use_container_width=True):
                    set_page('Admin')
                    st.rerun()



if st.session_state.page == "Landing":
    landing_page()
elif st.session_state.page == "Login":
    login_page()
elif st.session_state.page == "Register":
    register_page()
elif st.session_state.page == "User":
    user_page(st.session_state.username)
elif st.session_state.page == "Create Watchlist":
    create_watchlist_page(st.session_state.username)
elif st.session_state.page == "Friend Requests":
    friend_requests(st.session_state.username)
elif st.session_state.page == "Admin":
    admin_page()
elif st.session_state.page == "Database Handler":
    database_handler_page()
elif st.session_state.page == "Add Series":
    add_series_page(st.session_state.username)
elif st.session_state.page == "Table Data":
    table_data_page()
elif st.session_state.page == "Add Handler":
    add_handler_page()
