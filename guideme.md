# 🚀 StreamSync Setup Guide

This guide will walk you through setting up and running the StreamSync application step by step.

## 📋 Prerequisites

Before you begin, make sure you have the following installed on your system:

- **Python 3.8 or higher** ([Download Python](https://www.python.org/downloads/))
- **MySQL Server** ([Download MySQL](https://dev.mysql.com/downloads/mysql/))
- **Git** ([Download Git](https://git-scm.com/downloads))
- **MySQL Root Password** (you'll need this during setup)

> 💡 **Tip**: Make sure MySQL is running on your system before proceeding.

---

## 📦 Step 1: Clone the Repository

First, clone the repository to your local machine:

```bash
git clone <repository-url>
cd DBS_Project-Movies-and-Series-Watchlist-Manager
```

Or if you already have the repository, navigate to the project directory:

```bash
cd DBS_Project-Movies-and-Series-Watchlist-Manager
```

---

## 🐍 Step 2: Create a Virtual Environment

Navigate to the `Code` folder and create a virtual environment (on windows try to do in CMD as PowerShell sometimes gives error due to permission problems):

### For Windows:
```bash
cd Code
python -m venv venv
```

### For macOS/Linux:
```bash
cd Code
python3 -m venv venv
```

> 💡 **Note**: The virtual environment will be created in a folder named `venv` inside the `Code` directory.

---

## ✅ Step 3: Activate the Virtual Environment

Activate the virtual environment you just created:

### For Windows (PowerShell):
```powershell
.\venv\Scripts\Activate.ps1
```

### For Windows (Command Prompt):
```cmd
venv\Scripts\activate.bat
```

### For macOS/Linux:
```bash
source venv/bin/activate
```

> ✅ **Success Indicator**: You should see `(venv)` at the beginning of your command prompt, like this:
> ```
> (venv) C:\Users\YourName\...\Code>
> ```

---

## 📥 Step 4: Install Dependencies

With the virtual environment activated, install all required packages:

```bash
pip install -r requirements.txt
```

This will install all necessary dependencies including:
- Streamlit (for the web interface)
- mysql-connector-python (for database connectivity)
- Pandas (for data manipulation)
- And other required packages

> ⏱️ **Wait Time**: This may take a few minutes depending on your internet connection.

---

## 🗄️ Step 5: Set Up the Database

Now you need to create and populate the database. Run the database reset script:

```bash
python reset_database.py
```

### What happens next:

1. **Enter MySQL Password**: The script will prompt you to enter your MySQL root password:
   ```
   Enter MySQL password: 
   ```
   - Type your MySQL root password (it won't be visible for security)
   - Press Enter

2. **Database Creation**: The script will:
   - Drop the existing `Streamsync` database (if it exists)
   - Create a fresh `Streamsync` database
   - Create all necessary tables
   - Insert comprehensive sample data (movies, series, users, etc.)

3. **Wait for Completion**: The process may take a minute or two. You'll see progress messages like:
   ```
   🗑️  Dropping existing database...
   🆕 Creating new database...
   ✅ Database reset successful!
   📊 Creating tables...
   ✅ Tables created!
   🎬 Inserting comprehensive Bollywood/Indian data...
   ```

4. **Database Statistics**: At the end, you'll see a summary of what was created:
   ```
   📊 DATABASE STATISTICS
   ============================================================
     Total Users.........................    152
     Total Media Items...................     91
     ...
   ```

> ✅ **Success**: If you see "✅ Database setup completed successfully!" at the end, you're good to go!

---

## 🚀 Step 6: Run the Application

Now you're ready to launch the StreamSync web application!

### Start Streamlit:
go to prev directory
```bash
cd ..
```

```bash
streamlit run .\Code\app.py
```

### What happens:

1. **Browser Opens**: Streamlit will automatically open your default web browser
2. **Application URL**: You'll see something like:
   ```
   You can now view your Streamlit app in your browser.
   Local URL: http://localhost:8501
   Network URL: http://192.168.x.x:8501
   ```

---

## 🔐 Step 7: Enter Database Password in the App

When the application opens in your browser:

1. **Landing Page**: You'll see the StreamSync landing page
2. **Database Setup Section**: In the sidebar, find the "🔒 Database Setup" section
3. **Enter Password**: 
   - Enter your MySQL root password in the "Enter MySQL Password" field
   - Click outside the field or press Enter
   - You should see: "✅ Password saved! You can now login."

---

## 👤 Step 8: Login and Start Using

Now you can log in and start using the application!

### Default Login Credentials:

The database setup script creates default accounts:

#### Admin Account:
- **Username**: `admin`
- **Password**: `admin123`
- **Role**: Admin (full access)

#### Moderator Account:
- **Username**: `moderator`
- **Password**: `mod123`
- **Role**: Database Handler (can manage database)

#### User Accounts:
- **Username**: `user001` through `user150`
- **Password**: `password001` through `password150`
- **Role**: Regular user

### To Login:

1. Click the **"🔑 Login"** button on the landing page
2. Enter your username and password
3. Click **"🚀 Log In"**
4. You'll be redirected to your dashboard based on your role

---

## 🎉 You're All Set!

Congratulations! StreamSync is now running. You can:

- ✅ Browse movies and series
- ✅ Create playlists
- ✅ Track series progress
- ✅ Add friends
- ✅ Write reviews
- ✅ Explore recommendations

---

## 🛠️ Troubleshooting

### Issue: "Database connection error"

**Solution**: 
- Make sure MySQL Server is running
- Verify your MySQL root password is correct
- Check that MySQL is running on `localhost` with default port `3306`

### Issue: "Module not found" errors

**Solution**:
- Make sure the virtual environment is activated (you should see `(venv)` in your prompt)
- Reinstall dependencies: `pip install -r requirements.txt`

### Issue: "Port already in use"

**Solution**:
- Another Streamlit instance might be running
- Close other terminal windows running Streamlit
- Or use a different port: `streamlit run app.py --server.port 8502`

### Issue: Virtual environment activation fails

**Windows PowerShell**:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

Then try activating again.

### Issue: Database reset script fails

**Solution**:
- Ensure MySQL is running: Check MySQL service status
- Verify root user has necessary permissions
- Try running MySQL commands manually to test connection

---

## 📝 Additional Notes

- **Database Password**: You'll need to enter the MySQL password twice:
  1. Once when running `reset_database.py`
  2. Once in the Streamlit app's landing page

- **Stopping the Application**: Press `Ctrl+C` in the terminal to stop the Streamlit server

- **Re-running Database Setup**: You can run `reset_database.py` again anytime to reset the database with fresh data

- **Virtual Environment**: Always activate the virtual environment before running the application

---

## 🆘 Need Help?

If you encounter any issues not covered here:

1. Check that all prerequisites are installed correctly
2. Verify MySQL is running and accessible
3. Ensure Python version is 3.8 or higher
4. Check the terminal/console for error messages

---

**Happy Streaming! 🎬**

