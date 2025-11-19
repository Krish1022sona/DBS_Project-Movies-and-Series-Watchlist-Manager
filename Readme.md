# 🎥 StreamSync

<div align="center">

**A Smart Movies and Series Watchlist Manager**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.51.0-red.svg)](https://streamlit.io/)
[![MySQL](https://img.shields.io/badge/MySQL-8.0+-orange.svg)](https://www.mysql.com/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

*Track. Save. Discover.*

</div>

---

## 📖 About

**StreamSync** is a comprehensive, interactive web application built with **Streamlit** and **MySQL** that empowers users to manage, rate, and explore movies and series through a clean and modern interface. It's designed as a complete entertainment hub where users can create playlists, track viewing progress, connect with friends, and discover new content through intelligent recommendations.

---

## ✨ Key Features

### 🎞️ **Media Management**
- Browse extensive library of movies and TV series
- Detailed media information (genres, cast, crew, ratings)
- Advanced search and filtering capabilities
- Filter by genre, actor, director, release year, and ratings
- View top-rated content and recommendations

### 📋 **Playlist System**
- Create unlimited custom playlists
- Organize favorite content your way
- Add/remove items from playlists
- Share playlists with friends
- Track playlist statistics

### 📺 **Series Progress Tracking**
- Track which episode you last watched
- Resume watching from where you left off
- View progress across multiple series
- Episode-by-episode tracking

### ⭐ **Reviews & Ratings**
- Write detailed reviews for movies and series
- Rate content on a 1-10 scale
- View reviews from other users
- See average ratings for all content
- Top-rated content discovery

### 👥 **Social Features**
- Send and accept friend requests
- View friends' watchlists and activity
- See what friends are watching
- Discover content through friends' recommendations
- Mutual friends discovery

### 🧠 **Smart Recommendations**
- Personalized content suggestions
- Based on watch history and preferences
- Genre-based recommendations
- Friend activity-based suggestions
- Top-rated content discovery

### 🎛️ **Admin Dashboard**
- System metrics and statistics
- Activity log monitoring
- Database handler management
- User management capabilities

### 🗄️ **Database Handler Tools**
- Manage database tables
- Insert, update, and delete records
- View and edit table data
- Activity tracking and logging

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| **Frontend/UI** | Streamlit |
| **Backend** | Python 3.8+ |
| **Database** | MySQL 8.0+ |
| **Database Connector** | mysql-connector-python |
| **Data Processing** | Pandas |
| **Version Control** | Git & GitHub |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- MySQL Server
- Git

### Installation & Setup

**For detailed step-by-step setup instructions, please refer to [guideme.md](guideme.md)**

Quick overview:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd DBS_Project-Movies-and-Series-Watchlist-Manager
   ```

2. **Set up virtual environment**
   ```bash
   cd Code
   python -m venv venv
   ```

3. **Activate virtual environment**
   - Windows: `venv\Scripts\activate`
   - macOS/Linux: `source venv/bin/activate`

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up database**
   ```bash
   python reset_database.py
   ```

6. **Run the application**
   ```bash
   streamlit run app.py
   ```

> 📘 **Full Setup Guide**: See [guideme.md](guideme.md) for complete instructions with troubleshooting tips.

---

## 📁 Project Structure

```
DBS_Project-Movies-and-Series-Watchlist-Manager/
│
├── Code/
│   ├── app.py                 # Main Streamlit application
│   ├── reset_database.py      # Database setup script
│   ├── data.py                # Data utilities
│   ├── requirements.txt       # Python dependencies
│   └── dbs_proj.sql          # SQL schema file
│
├── Resources/                 # Images and assets
├── E-R Model/                 # Database entity-relationship diagrams
├── guideme.md                # Detailed setup guide
└── README.md                 # This file
```

---

## 🎯 Default Accounts

After running the database setup, you can log in with:

| Role | Username | Password |
|------|----------|----------|
| **Admin** | `admin` | `admin123` |
| **Moderator** | `moderator` | `mod123` |
| **User** | `user001` - `user150` | `password001` - `password150` |

---

## 📊 Database Schema

The application uses a comprehensive MySQL database with the following main tables:

- **Users** - User accounts and profiles
- **Media** - Movies and series information
- **Episodes** - Series episode details
- **Playlist** - User-created playlists
- **Reviews_Table** - User reviews and ratings
- **Friends** - Friend relationships
- **Series_Progress_Table** - User viewing progress
- **Media_Cast** & **Media_Crew** - Cast and crew information
- **Activity_Log** - System activity tracking

For detailed schema information, see `Code/dbs_proj.sql`

---

## 🎨 Features in Detail

### User Dashboard
- Personalized home page with statistics
- Quick access to watchlists, series progress, and friends
- Recommendations based on viewing history
- Continue watching section

### Explore Page
- Advanced search functionality
- Multi-criteria filtering (genre, people, type, rating)
- Search across titles, cast, crew, and genres
- Paginated results

### Watchlist Management
- Create multiple playlists
- Add/remove media items
- Organize content by preference
- View playlist statistics

### Series Progress
- Track episode-by-episode progress
- Resume from last watched episode
- View all series in progress
- Update progress easily

### Social Features
- Send friend requests
- Accept/decline requests
- View friends' activity
- Discover content through friends

---

## 🔒 Security Features

- Password hashing using SHA-256
- Role-based access control (Admin, Moderator, User)
- Activity logging for audit trails
- Secure database connections
- Input validation and sanitization

---

## 📈 Performance Optimizations

- Database connection pooling
- Optimized SQL queries with JOINs
- Cached CSS and static content
- Efficient session state management
- Pagination for large datasets

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

## 📝 License

This project is licensed under the MIT License.

---

## 👨‍💻 Development

### Code Structure

- **app.py**: Main application file with all Streamlit pages and functions
- **reset_database.py**: Database initialization and data seeding
- **data.py**: Data utility functions

### Key Functions

- Database operations: `execute_query()`, `get_db_connection()`
- User management: `authenticate_user()`, `register_user()`
- Media operations: `search_media()`, `get_media_full_details()`
- Social features: `send_friend_request()`, `get_friends()`

---

## 🐛 Known Issues

None at the moment. If you find any issues, please report them.

---

## 📞 Support

For setup help, troubleshooting, or questions:
- Check [guideme.md](guideme.md) for detailed setup instructions
- Review the troubleshooting section in the guide

---

## 🎉 Acknowledgments

- Built with [Streamlit](https://streamlit.io/)
- Database powered by [MySQL](https://www.mysql.com/)
- Icons and UI elements from Streamlit components

---

<div align="center">

**Made with ❤️ for movie and series enthusiasts**

[Get Started →](guideme.md)

</div>
