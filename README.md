# Smart-Fee-Scheduling-Reminder-System-for-Private-Tuitions-Tutors-
This project is a Python-based automated email reminder system that sends invoice reminders, due notices, and overdue alerts to users based on CSV data.
It also tracks email opens, link clicks, and performance metrics, and supports automatic daily scheduling.

🚀 Features
📬 Automated Reminder, Due, and Overdue invoice emails
📊 Email open & click tracking
📁 CSV-based user & invoice management
📎 Attachment support
⏰ Daily scheduled execution
🌍 Timezone & holiday-aware scheduling
🔁 Retry logic for failed emails
📈 Metrics logging (open rate, click rate, send stats)

## 📦 Installation & Setup
### Prerequisites
Make sure the following are installed on your system:
- Python 3.8+
- pip package manager
- Gmail account with App Password enabled
- Internet connection (SMTP + tracking)

### Step 1: Clone the Repository
git clone https://github.com/Sanket3332/Smart-Fee-Scheduling-Reminder-System-for-Private-Tuitions-Tutors.git
cd Smart-Fee-Scheduling-Reminder-System-for-Private-Tuitions-Tutors

### Step 2: Create Virtual Environment
# For Windows
python -m venv venv
venv\Scripts\activate

# For Mac/Linux
python3 -m venv venv
source venv/bin/activate

Step 3: Install Dependencies
Install all dependencies using:
pip install pandas flask python-dotenv schedule pytz holidays apscheduler
pip install -r requirements.txt

Step 4: Configuration
Copy .env to .env
Update the configuration values in .env

1️⃣ Update File Paths
Update the following paths in the code according to your system:
ATTACHMENT_PATHS = ["path/to/images.png"]
CSV_PATH = "path/to/Emails.csv"
TRACKING_FILE = "path/to/email_tracking.csv"
CLICKING_FILE = "path/to/click_tracking.csv"
METRICS_FILE = "path/to/metrics.csv"

2️⃣ Email (SMTP) Configuration
Update the SMTP credentials:
Sender_email = "your_email@gmail.com"
Email_pass = "your_gmail_app_password"
Server = "smtp.gmail.com"
Port = 587

Step 5: Run the Application
🔹 Manual Run
Run the script manually using:
python main.py

🚀 Quick Start (For Immediate Testing)
git clone https://github.com/your-username/your-repo.git
cd your-repo
pip install -r requirements.txt
python main.py

🌐 Tracking Server

The project uses Flask routes:
/open?tid=<tracking_id>
/click?tid=<tracking_id>

🛠️ Troubleshooting
Common Issues:

Issue: ModuleNotFoundError
Solution: Ensure all dependencies are installed: pip install -r requirements.txt

Issue: Port already in use
Solution: Change port in config or kill process using port:

# Linux/Mac
lsof -ti:8080 | xargs kill -9

# Windows
netstat -ano | findstr :8080
taskkill /PID [PID] /F
