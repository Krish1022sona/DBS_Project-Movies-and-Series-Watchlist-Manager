import streamlit as st
from streamlit_option_menu import option_menu


# initialize
if 'page' not in st.session_state:
    st.session_state.page ="Landing"
if 'username' not in st.session_state:
    st.session_state.username = ""
if 'selected_table' not in st.session_state:
    st.session_state.selected_table = ""
if 'handlers' not in st.session_state:
    st.session_state.handlers = [
        {"name": "Krishna", "year": 2023, "role": "Senior Handler"},
        {"name": "Alice", "year": 2022, "role": "Data Analyst"},
        {"name": "Bob", "year": 2021, "role": "Backup Handler"},
        {"name": "Charlie", "year": 2020, "role": "Lead Handler"}
    ]



def set_page(page):
    st.session_state.page = page


def landing_page():
    st.set_page_config(page_title="WatchPlan", page_icon="🎥", layout="centered")

    st.title("🎥 WatchPlan")
    st.subheader("Track. Save. Discover")
    st.divider()

    st.sidebar.subheader("Start Tracking Now")

    if st.sidebar.button(label="Login", use_container_width=True):
        set_page('Login')
        st.rerun()
    
    if st.sidebar.button(label="Register", use_container_width=True):
        set_page('Register')
        st.rerun()

    

    with st.container():
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.subheader("explore in the vast library of movies, series, and you name it we have it".title())

        with col2:
            st.image(image="Resources/vast_library.png", width="stretch")

    with st.container():
        col1, col2 = st.columns([3, 4])
        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.subheader("track your interests with custom playlists".title())

        with col1:
            st.image(image="Resources/playlist_tracking.png", width="stretch")
    
    with st.container():
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.subheader("make like minded friends and take suggestions".title())

        with col2:
            st.image(image="Resources/friends.png", width="stretch")
    
    st.divider()
    if st.button(label="Take Me With You", use_container_width=True):
        set_page('Login')
        st.rerun()

def login_page():
    st.title("welcome back, wait who were you again?".title())
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
    
        if st.form_submit_button("Log In"):
            st.session_state.username = username
            if username == 'admin':
                set_page('Admin')
                st.rerun()
            elif username == 'dataguy':
                set_page('Database Handler')
                st.rerun()
            else:
                set_page('User')
                st.rerun()

def register_page():
    st.title("ready to start your watchlist. let's go".title())
    with st.form("register_form"):
        with st.container():
            col1, col2 = st.columns([1,1])
            with col1:
                first_name = st.text_input("First Name")
            with col2:
                last_name = st.text_input("Last Name")

        with st.container():
            col1, col2 = st.columns([1,1])
            with col1:
                username = st.text_input("Username")
            with col2:
                mail_id = st.text_input("Email")

        with st.container():
            col1, col2 = st.columns([1,1])
            with col1:
                password = st.text_input("Password", type="password")
            with col2:
                confirm_password = st.text_input("Confirm Password", type="password")
    
        if st.form_submit_button("Register"):
            st.session_state.username = username
            set_page('User')
            st.rerun()



def user_page(username):
    with st.sidebar:
        selected = option_menu(
            menu_title="WatchPlan",
            options=["Home", "Explore", "Watchlist", "Series Progress", "Friends"],
            icons=["house", "search", "film", "tv", "people"],
            menu_icon="camera-reels",
            default_index=0,
            styles={
                "container": {"background-color": "#0E1117"},
                "icon": {"color": "#FF4B4B", "font-size": "20px"},
                "nav-link-selected": {"background-color": "#262730"},
            },
        )

    st.sidebar.divider()
    st.sidebar.button(label="LOG OUT", on_click=set_page, args=('Landing',))


    if selected == "Home":
        st.title(f"Welcome {st.session_state.username}")
        st.divider()

        with st.container():
            col1, col2 = st.columns([2,1])
            with col1:
                with st.container(border=True):
                    st.subheader("take some suggestions from us".title())
            with col2:
                with st.container(border=True):
                    st.subheader("continue your last watched episode".title())

        with st.container():
            col1, col2 = st.columns([1,1])
            with col1:
                with st.container(border=True):
                    st.subheader("one of your recent watchlist".title())
            with col2:
                with st.container(border=True):
                    st.subheader("another of your recent watchlist".title())

    elif selected == "Explore":
        st.title("Explore")
        with st.container():
            query = st.text_input("type to search".title())
            options = ["All", "Movies", "Series", "Episodes", "Genre", "Cast & Crew"]

            cols = st.columns([1, 1, 1, 1, 1, 2])
            selected = []
            for col, option in zip(cols, options):
                with col:
                    if st.checkbox(option, key=option):
                        selected.append(option)

        with st.container(border=True):
            st.subheader("here the output will come".title())

    elif selected == "Watchlist":
        with st.container():
            col1, col2 = st.columns([5, 2])
            with col1:
                st.title("Your Watchlist")
            with col2:
                st.write("")
                if st.button(label="Create New", use_container_width=True):
                    set_page('Create Watchlist')
                    st.rerun()

        st.divider()

        with st.container():
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.container(border=True):
                    st.subheader("Watchlist 1: Your Favorite Movies")
                    st.write("Dummy content: List of movies in this watchlist.")
            with col2:
                with st.container(border=True):
                    st.subheader("Watchlist 2: Must-Watch Series")
                    st.write("Dummy content: List of series in this watchlist.")

        with st.container():
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.container(border=True):
                    st.subheader("Watchlist 3: Action Pack")
                    st.write("Dummy content: Action movies and shows.")
            with col2:
                with st.container(border=True):
                    st.subheader("Watchlist 4: Comedy Central")
                    st.write("Dummy content: Funny stuff here.")
    elif selected == "Series Progress":
        with st.container():
            col1, col2 = st.columns([5, 2])
            with col1:
                st.title("Your Series Progress")
            with col2:
                st.write("")
                if st.button(label="Add Series", use_container_width=True):
                    set_page('Add Series')
                    st.rerun()

        st.divider()

        with st.container():
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.container(border=True):
                    st.subheader("Series 1: Breaking Bad")
                    st.write("Progress: Season 5, Episode 10")
            with col2:
                with st.container(border=True):
                    st.subheader("Series 2: Game of Thrones")
                    st.write("Progress: Season 8, Episode 6")

        with st.container():
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.container(border=True):
                    st.subheader("Series 3: The Office")
                    st.write("Progress: Season 9, Episode 25")
            with col2:
                with st.container(border=True):
                    st.subheader("Series 4: Stranger Things")
                    st.write("Progress: Season 4, Episode 9")
    elif selected == "Friends":
        with st.container():
            col1, col2 = st.columns([5, 2])
            with col1:
                st.title("Friends")
            with col2:
                st.write("")
                if st.button(label="Requests", use_container_width=True):
                    set_page("Friend Requests")
                    st.rerun()

        st.divider()

        with st.container():
            col1, col2 = st.columns([1, 1])
            with col1:
                with st.container(border=True):
                    st.subheader("here your friends will comeup, once you have them".title())
            with col2:
                with st.container(border=True):
                    st.subheader("here you can search people and make them your friends".title())

def add_series_page(username):
    st.title("Add Series")

    if st.button("Go Back", use_container_width=True):
        set_page('User')
        st.rerun()

    st.divider()

    with st.container():
        query = st.text_input("type to search for series".title())
        options = ["All", "Series", "Genre", "Cast & Crew"]

        cols = st.columns([1, 1, 1, 2])
        selected = []
        for col, option in zip(cols, options):
            with col:
                if st.checkbox(option, key=f"add_{option}"):
                    selected.append(option)

    with st.container(border=True):
        st.subheader("here the series search results will come".title())

def create_watchlist_page(username):
    with st.container():
        col1, col2 = st.columns([5, 2])
        with col1:
            st.title("Create New Watchlist")
        with col2:
            st.write("")
            if st.button(label="Go Back", use_container_width=True):
                set_page('User')
                st.rerun()

    st.divider()

    with st.form("create_watchlist_form"):
        watchlist_name = st.text_input("Watchlist Name")
        if st.form_submit_button("Create"):
            st.success(f"Watchlist '{watchlist_name}' created successfully!")
            set_page('User')
            st.rerun()

def friend_requests(username):
    with st.container():
        col1, col2 = st.columns([5, 2])
        with col1:
            st.title("Friend Requests")
        with col2:
            st.write("")
            if st.button(label="Go Back", use_container_width=True):
                set_page('User')
                st.rerun()

    st.divider()

    with st.container(border=True):
        st.subheader("here all your friend requests will show up".title())


def admin_page():
    with st.sidebar:
        selected = option_menu(
            menu_title="WatchPlan",
            options=["Home", "Changes", "Database Handlers"],
            icons=["house", "search", "people"],
            menu_icon="camera-reels",
            default_index=0,
            styles={
                "container": {"background-color": "#0E1117"},
                "icon": {"color": "#FF4B4B", "font-size": "20px"},
                "nav-link-selected": {"background-color": "#262730"},
            },
        )

    st.sidebar.divider()
    st.sidebar.button(label="LOG OUT", on_click=set_page, args=('Landing',))

    if selected == "Home":
        st.title("🎛️ Admin Dashboard")
        st.markdown("Welcome to the Admin Dashboard! Monitor system performance and manage key operations.")
        st.divider()

        st.header("📊 System Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Users", value="1500", delta="10%")
        with col2:
            st.metric(label="Active Sessions", value="200", delta="-5%")
        with col3:
            st.metric(label="Recent Changes", value="Last update: 2023-10-01")
        with col4:
            st.metric(label="System Health", value="Operational")

        st.write("")
        st.info("💡 Tip: Keep an eye on active sessions for optimal performance.")

    elif selected == "Changes":
        st.title("🔄 Changes")
        st.markdown("Track all recent database changes and operations performed by handlers.")
        st.divider()

        changes_data = {
            "Handler": ["Krishna", "Alice", "Bob", "Charlie"],
            "Change": ["Added media: Inception", "Updated user: john_doe", "Deleted review: rev123", "Migrated data"],
            "Operation": ["INSERT", "UPDATE", "DELETE", "UPDATE"],
            "Table": ["Media", "Users", "Reviews_Table", "Media"],
            "Time": ["2023-10-01", "2023-09-30", "2023-09-29", "2023-09-28"]
        }
        st.table(changes_data)

        st.write("")
        st.success("✅ All changes are logged and monitored for audit purposes.")

    elif selected == "Database Handlers":
        st.title("👥 Database Handlers")
        st.markdown("Manage and view all active database handlers.")
        st.divider()

        col1, col2 = st.columns([3, 1])
        with col1:
            st.header("Active Handlers")
        with col2:
            if st.button(label="➕ Add Handler", use_container_width=True):
                set_page('Add Handler')
                st.rerun()

        st.write("")

        for handler in st.session_state.handlers:
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.subheader(f"👤 {handler['name']}")
                    st.write(f"🟢 Active since {handler['year']}")
                    st.write(f"Role: {handler['role']}")
            # Leave col2 empty for now, can add more info later

        st.write("")
        st.info("💡 Handlers ensure data integrity and perform maintenance tasks.")

def database_handler_page():
    with st.sidebar:
        selected = option_menu(
            menu_title="WatchPlan",
            options=["Home", "Changes", "Database", "Database Handlers"],
            icons=["house", "search", "tv", "people"],
            menu_icon="camera-reels",
            default_index=0,
            styles={
                "container": {"background-color": "#0E1117"},
                "icon": {"color": "#FF4B4B", "font-size": "20px"},
                "nav-link-selected": {"background-color": "#262730"},
            },
        )

    st.sidebar.divider()
    st.sidebar.button(label="LOG OUT", on_click=set_page, args=('Landing',))

    if selected == "Home":
        st.title("🗄️ Database Handler Dashboard")
        st.markdown("Manage and monitor database operations efficiently.")
        st.divider()

        st.header("📈 Database Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric(label="Total Tables", value="50", delta="2")
        with col2:
            st.metric(label="Active Connections", value="10", delta="1")
        with col3:
            st.metric(label="Recent Queries", value="SELECT * FROM users")
        with col4:
            st.metric(label="Database Health", value="Operational")

        st.write("")
        st.info("💡 Optimize queries to maintain high performance.")

    elif selected == "Changes":
        st.title("🔄 Changes")
        st.markdown("Track all recent database changes and operations performed by handlers.")
        st.divider()

        changes_data = {
            "Handler": ["Krishna", "Alice", "Bob", "Charlie"],
            "Change": ["Added media: Inception", "Updated user: john_doe", "Deleted review: rev123", "Migrated data"],
            "Operation": ["INSERT", "UPDATE", "DELETE", "UPDATE"],
            "Table": ["Media", "Users", "Reviews_Table", "Media"],
            "Time": ["2023-10-01", "2023-09-30", "2023-09-29", "2023-09-28"]
        }
        st.table(changes_data)

        st.write("")
        st.success("✅ All changes are logged and monitored for audit purposes.")

    elif selected == "Database":
        st.title("🗃️ Database")
        st.markdown("Access and manage all database tables.")
        st.divider()

        st.header("Available Tables")
        tables = ["Users", "Media", "genres", "Episodes", "Watchlists_item", "playlist", "Playlist_item", "Media_Genres", "Series_Progress_Table", "Reviews_Table", "Friends", "People", "Media_Cast", "Media_Crew", "Activity_Log"]

        cols = st.columns(3)
        for i, table in enumerate(tables):
            with cols[i % 3]:
                if st.button(label=f"📋 {table}", use_container_width=True):
                    st.session_state.selected_table = table
                    set_page('Table Data')
                    st.rerun()

        st.write("")
        st.info("💡 Click on a table to view and edit its data.")

    elif selected == "Database Handlers":
        st.title("👥 Database Handlers")
        st.markdown("Manage and view all active database handlers.")
        st.divider()

        st.header("Active Handlers")

        st.write("")

        for handler in st.session_state.handlers:
            col1, col2 = st.columns(2)
            with col1:
                with st.container(border=True):
                    st.subheader(f"👤 {handler['name']}")
                    st.write(f"🟢 Active since {handler['year']}")
                    st.write(f"Role: {handler['role']}")
            # Leave col2 empty for now, can add more info later

        st.write("")
        st.info("💡 Handlers ensure data integrity and perform maintenance tasks.")

def table_data_page():
    table_name = st.session_state.get('selected_table', 'Users')
    st.title(f"Data in {table_name}")

    if st.button("Go Back", use_container_width=True):
        set_page('Database Handler')
        st.rerun()

    st.divider()

    # Dummy data display
    st.subheader("Table Data")
    st.write("Dummy data: Sample records from the table.")

    # Insert form
    st.subheader("Insert New Record")
    with st.form(f"insert_{table_name}"):
        # Dummy fields
        st.text_input("Field 1")
        st.text_input("Field 2")
        if st.form_submit_button("Insert"):
            st.success("Record inserted successfully!")

    # Update form
    st.subheader("Update Record")
    with st.form(f"update_{table_name}"):
        st.text_input("Record ID")
        st.text_input("Field to Update")
        st.text_input("New Value")
        if st.form_submit_button("Update"):
            st.success("Record updated successfully!")

def add_handler_page():
    st.title("Add New Handler")

    if st.button("Go Back", use_container_width=True):
        set_page('Admin')
        st.rerun()

    st.divider()

    with st.form("add_handler_form"):
        username = st.text_input("Username")

        if st.form_submit_button("Add Handler"):
            new_handler = {"name": username, "year": 2024, "role": "Data Analyst"}
            st.session_state.handlers.append(new_handler)
            st.success(f"Handler '{username}' added successfully!")
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
