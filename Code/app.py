import streamlit as st


# initialize 
if 'page' not in st.session_state:
    st.session_state.page ="Landing"
if 'username' not in st.session_state:
    st.session_state.username = ""



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
            st.image(image="..\\Resources\\vast_library.png", width="stretch")

    with st.container():
        col1, col2 = st.columns([3, 4])
        with col2:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.subheader("track your interests with custom playlists".title())

        with col1:
            st.image(image="..\\Resources\\playlist_tracking.png", width="stretch")
    
    with st.container():
        col1, col2 = st.columns([3, 2])
        with col1:
            st.write("")
            st.write("")
            st.write("")
            st.write("")
            st.subheader("make like minded friends and take suggestions".title())

        with col2:
            st.image(image="..\\Resources\\friends.png", width="stretch")
    
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
            set_page('User')
            st.rerun()

def register_page():
    st.title("ready to start your watchlist. let's go".title())
    with st.form("register_form"):
        mail_id = st.text_input("Email")
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
                password = st.text_input("Password", type="password")
    
        if st.form_submit_button("Register"):
            st.session_state.username = username
            set_page('User')
            st.rerun()



def user_page(username):
    from streamlit_option_menu import option_menu
    import streamlit as st

    with st.sidebar:
        selected = option_menu(
            menu_title="WatchPlan",
            options=["Home", "Watchlist", "Series Progress", "Friends"],
            icons=["house", "film", "tv", "people"],
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
    elif selected == "Watchlist":
        pass
    elif selected == "Series Progress":
        pass
    elif selected == "Friends":
        pass

def admin_page():
    st.title("Aye Aye Admin")

def database_handler_page():
    st.title("Get. Set. Job")



if st.session_state.page == "Landing":
    landing_page()
elif st.session_state.page == "Login":
    login_page()
elif st.session_state.page == "Register":
    register_page()
elif st.session_state.page == "User":
    user_page(st.session_state.username)
elif st.session_state.page == "Admin":
    admin_page()
elif st.session_state.page == "Databse Handler":
    database_handler_page()