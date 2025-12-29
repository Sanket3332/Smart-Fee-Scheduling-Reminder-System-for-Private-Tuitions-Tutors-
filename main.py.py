import os
from dotenv import load_dotenv
import pandas as pd
import smtplib, time, uuid, csv
from datetime import date, datetime, timedelta
from email.message import EmailMessage
from email.utils import formataddr
import schedule, pytz, holidays 
from apscheduler.schedulers.blocking import BlockingScheduler
from flask import Flask, request   

#CONFIGURATION

ATTACHMENT_PATHS = 
CSV_PATH = 

# TIMEZONE CONFIGURATION
TIMEZONE = pytz.timezone("Europe/Berlin")   # change if needed

# HOLIDAY CONFIGURATION (Germany example)
HOLIDAYS = holidays.Germany()

# RETRY CONFIGURATION
MAX_RETRIES = 3
RETRY_DELAY = 5  # seconds

app = Flask(__name__)

#SMTP CONFIGURATION (REQUIRED)

Sender_email = ""       # your sender email
Email_pass = ""         # your email app password
Server = "smtp.gmail.com"                     # your SMTP server
Port = 587                                    # your SMTP port

TRACKING_FILE = 
CLICKING_FILE = 
METRICS_FILE = 


#UTILITIES

def load_csv(path):
    return pd.read_csv(
        path, parse_dates=["Due", "Reminder"], 
        date_format= "%d-%m-%Y")

def adjust_date(d):
    if d is None or pd.isna(d):
        return None

    if isinstance(d, str):
        d= pd.to_datetime(d,dayfirst = True, errors = "coerce")

    if pd.isna(d):
        return None

    d= d.normalize()

    while d.weekday() >= 5 or d in HOLIDAYS:
        d += pd.Timedelta(days=1)
    return d

def write_csv(file, headers, row):
    with open(file, "a", newline="") as f:
        writer = csv.writer(f)
        if f.tell() == 0:
            writer.writerow(headers)
        writer.writerow(row)

def log_sent(tracking_id, email):
    write_csv(TRACKING_FILE, ["tracking_id", "email", "timestamp"], 
              [tracking_id, email, datetime.now()])

def log_open(tracking_id, event):
    write_csv(CLICKING_FILE, ["tracking_id", "event_type", "timestamp"], 
              [tracking_id, "open", datetime.now()])

def log_click(tracking_id, event):
    write_csv(CLICKING_FILE, ["tracking_id", "event_type", "timestamp"], 
              [tracking_id, "click", datetime.now()])

def log_metric(metric, value):
    write_csv(METRICS_FILE, ["date", "metric", "value"],
              [datetime.now().date(), metric, value])
    

    #TRACKING ROUTES

@app.route("/open")
def track_open():
    tid = request.args.get("tid")
    if tid:
        log_open(tid, "open")
    # Return 1x1 transparent gif
    return b"\x47\x49\x46\x38\x39\x61\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02\x44\x01\x00\x3b", 200, {"Content-Type": "image/gif"}

@app.route("/click")
def track_click():
    tid = request.args.get("tid")
    if tid:
        log_click(tid, "click")
    return '<meta http-equiv="refresh" content="0:url=https://www.paypal.com/signin">'


#METRICS

def compute_open_click_rates():
    sent = pd.read_csv(TRACKING_FILE)
    events = pd.read_csv(CLICKING_FILE)
    
    total_sent = len(sent)
    total_opened = len(events[events["event_type"]=="open"])
    total_clicked = len(events[events["event_type"]=="click"])
    
    open_rate = round((total_opened/total_sent)*100, 2) if total_sent else 0
    click_rate = round((total_clicked/total_sent)*100, 2) if total_sent else 0
 
    print(f"Open Rate: {open_rate}%, Click Rate: {click_rate}%")
    log_metric("open_rate", open_rate)
    log_metric("click_rate", click_rate)


##1st Try
def Reminder(Subject, Receiver_emails, Name, Due, Invoice, Amount, tracking_id):
    #create the base text message
        msg = EmailMessage()
        msg["Subject"] = Subject
        msg["From"] = formataddr(("IUBH University", f"{Sender_email}"))
        msg["To"] = Receiver_emails
          

        #HTML Version 
        tracking_pixel = f"https://your-tracking-server.com/open?tid={tracking_id}"
        click_url = f"https://www.paypal.com/signin/click?tid={tracking_id}"
        
        msg.add_alternative(
            f"""\
        <html>

        <head>
            <h1>Invoice Payment Reminder Email</h1>

        </head>

          <body>

            <h2>Dear {Name},</h2>
            <p>I trust this email finds you well.</p>
            <p>I would like to remind you about your upcoming payment for invoice <strong>{Invoice}</strong>. 
            The total amount due is <strong>{Amount}</strong>, and the due date is <strong>{Due}</strong>.</p>
            <p>To make the payment process as convenient as possible, please use the following payment button.</p> 
            <p>Should you have any questions or require assistance regarding your invoice, please don't hesitate to reach out to our dedicated support team at <strong>https://www.iu.org/contact/</strong></p>
            <p>Thank you for your prompt attention to this matter. We genuinely appreciate your continued partnership.</p>
            
            <a href= "{click_url}">
              <button style="padding:20px;background:green;color:white"><strong>Pay Now {Amount} </strong></button>
            </a>
            
            <img src="{tracking_pixel}" width="1" height="1" style="display:none;">
            
            <h3>Best regards,</h3>

            <p><strong>Sanket Madavi</strong></p>
            <p><strong>Computer Science Master Student</strong></p>
            <p><strong>IU International University of Applied Science</strong></p>
            <p><strong>https://www.iu.de/hochschule/mycampus/</strong></p>

          </body>

        </html>
        """,
          subtype = "html", 
        )


#Attachment Hnadling      
        for file in ATTACHMENT_PATHS:
            try:
                with open(file, 'rb') as attach:
                    file_data = attach.read()
                    #file_type = imghdr.what(attachment.name)
                    file_name = attach.name 
                
                msg.add_attachment(file_data, maintype = 'application', subtype = 'octet-stream', filename = file_name)

            except Exception as e:
                print(f"⚠ Could not attach file {file_path}: {e}")


# Retry Logic
        for attempt in range(MAX_RETRIES):
            try:
                with smtplib.SMTP(Server, Port) as Protocol:
                    print("Connected to SMTP server")
                    Protocol.starttls()
                    print("TLS Started")
                    Protocol.login(Sender_email, Email_pass)
                    print("SMTP Login Success")
                    Protocol.sendmail(Sender_email, Receiver_emails, msg.as_string())
                    print(f"Email sent → {Receiver_emails}")
                    Protocol.close() 
                return True
            except Exception as e:
                print(f"❌ Email sending attempt {attempt+1} failed: {e}")
                time.sleep(RETRY_DELAY)
        
        return False


def date_loading(CSV_PATH):
        return pd.read_csv(CSV_PATH, parse_dates = ['Due', 'Reminder'], dayfirst = True)
        

def Process_Reminder(dates):
    today = adjust_date(pd.Timestamp(datetime.now(TIMEZONE).date())).date()
    Email_Count = 0
    failed_count = 0
    start_time = time.time()

    for _, row in dates.iterrows():
            if row['Paid'] == 'No' and adjust_date(row["Reminder"]).date() == today:
                tid = str(uuid.uuid4())
                Reminder(
                    Subject = f'Friendly Reminder: Invoice Payment Due Soon',
                    Receiver_emails = row['Email-ID'],
                    Name = row['Name'],
                    Due = row['Due'].strftime("%d %m %Y"),
                    Invoice = row['Invoice'],
                    Amount = row['Amount'],
                    tracking_id = tid
                )
                log_sent(tid, row["Email-ID"])
                Email_Count += 1   
             
            else:
                failed_count += 1
                duration = round(time.time() - start_time, 2)
    
    log_metric("emails_sent", Email_Count)
    log_metric("emails_failed", failed_count)
    log_metric("processing_time_seconds", duration)
                
    print("Scaning for User's Reminder date..")
    return(f"Total Reminder Emails Sent: {Email_Count}, ❌ Failed: {failed_count}, ⏱ Duration: {duration}s")
    

#SCHEDULER
def schedule_daily_reminder(hour=9, minute=00):
    """Schedules the process_reminders function to run daily at given time."""
    time_str = f"{hour:02d}:{minute:02d}"
    schedule.every().day.at(time_str).do(Process_Reminder, dates) 
    print(f"📅 Scheduled automatic run daily at {time_str} {TIMEZONE} timezone")

    while True:
        schedule.run_pending()
        time.sleep(10)  # Check every 30 seconds

try:
    dates = date_loading(CSV_PATH)
    print(dates)
    print("Running Script Manually now.")
    result = Process_Reminder(dates)
    print(result)
    print("Starting Scheduler for automatic daily reminders")
    schedule_daily_reminder(hour=9, minute=00)


except Exception as e:
    print("❌ Main Error:", e)    
   

   ##2nd Try
def Due(Subject, Receiver_emails, Name, Due, Invoice, Amount, tracking_id):
    #create the base text message
        msg = EmailMessage()
        msg["Subject"] = Subject
        msg["From"] = formataddr(("IUBH University", f"{Sender_email}"))
        msg["To"] = Receiver_emails
          

        #HTML Version 
        tracking_pixel = f"https://your-tracking-server.com/open?tid={tracking_id}"
        click_url = f"https://www.paypal.com/signin/click?tid={tracking_id}"
        
        msg.add_alternative(
            f"""\
        <html>

        <head>
            <h1>Invoice Payement Due Email</h1>

        </head>

          <body>

            <h2>Dear {Name},</h2>
            <p>I trust this email finds you well.</p>
            <p>This is a urgent reminder that your invoice <strong>{Invoice}</strong> in the amount of <strong>{Amount}</strong> is due today, <strong>{Due}</strong>.</p> 
            <p>To ensure uninterrupted service and a hassle-free experience, please take a moment to complete your payment. 
            You can settle the invoice by clicking on the following payment button.</p> 
            <p>If you've already made the payment, kindly disregard this reminder.</p>
            <p>Should you require any assistance or have questions, regarding your invoice, our dedicated support team is ready to assist. Contact us at <strong>https://www.iu.org/contact/</strong></p>
            <p>Thank you for your prompt attention to this matter. We genuinely appreciate your continued partnership.</p>
            
            <a href= "{click_url}">
              <button style="padding:20px;background:blue;color:white"><strong>Pay Now {Amount} </strong></button>
            </a>
            
            <img src="{tracking_pixel}" width="1" height="1" style="display:none;">
            
            <h3>Best regards,</h3>

            <p><strong>Sanket Madavi</strong></p>
            <p><strong>Computer Science Master Student</strong></p>
            <p><strong>IU International University of Applied Science</strong></p>
            <p><strong>https://www.iu.de/hochschule/mycampus/</strong></p>

          </body>

        </html>
        """,
          subtype = "html", 
        )


#Attachment Hnadling      
        for file in ATTACHMENT_PATHS:
            try:
                with open(file, 'rb') as attach:
                    file_data = attach.read()
                    #file_type = imghdr.what(attachment.name)
                    file_name = attach.name 
                
                msg.add_attachment(file_data, maintype = 'application', subtype = 'octet-stream', filename = file_name)

            except Exception as e:
                print(f"⚠ Could not attach file {file_path}: {e}")


# Retry Logic
        for attempt in range(MAX_RETRIES):
            try:
                with smtplib.SMTP(Server, Port) as Protocol:
                    print("Connected to SMTP server")
                    Protocol.starttls()
                    print("TLS Started")
                    Protocol.login(Sender_email, Email_pass)
                    print("SMTP Login Success")
                    Protocol.sendmail(Sender_email, Receiver_emails, msg.as_string())
                    print(f"Email sent → {Receiver_emails}")
                    Protocol.close() 
                return True
            except Exception as e:
                print(f"❌ Email sending attempt {attempt+1} failed: {e}")
                time.sleep(RETRY_DELAY)
        
        return False


def date_loading(CSV_PATH):
        return pd.read_csv(CSV_PATH, parse_dates = ['Due', 'Reminder'], dayfirst = True)
        

def Process_Due(dates):
    today = adjust_date(pd.Timestamp(datetime.now(TIMEZONE).date())).date()
    Email_Count = 0
    failed_count = 0
    start_time = time.time()

    for _, row in dates.iterrows():
            if row['Paid'] == 'No' and adjust_date(row["Due"]).date() == today:
                tid = str(uuid.uuid4())
                Due(
                    Subject = f'Urgent Reminder: Invoice Payment Due Today',
                    Receiver_emails = row['Email-ID'],
                    Name = row['Name'],
                    Due = row['Due'].strftime("%d %m %Y"),
                    Invoice = row['Invoice'],
                    Amount = row['Amount'],
                    tracking_id = tid
                )
                log_sent(tid, row["Email-ID"])
                Email_Count += 1   
             
            else:
                failed_count += 1
                duration = round(time.time() - start_time, 2)
    
    log_metric("emails_sent", Email_Count)
    log_metric("emails_failed", failed_count)
    log_metric("processing_time_seconds", duration)
                
    print("Scaning for User's Due date..")
    return(f"Total Due Emails Sent: {Email_Count}, ❌ Failed: {failed_count}, ⏱ Duration: {duration}s")
    

#SCHEDULER
def schedule_daily_due(hour=9, minute=00):
    """Schedules the Process_Due function to run daily at given time."""
    time_str = f"{hour:02d}:{minute:02d}"
    schedule.every().day.at(time_str).do(Process_Due, dates) 
    print(f"📅 Scheduled automatic run daily at {time_str} {TIMEZONE} timezone")

    while True:
        schedule.run_pending()
        time.sleep(10)  # Check every 30 seconds

try:
    dates = date_loading(CSV_PATH)
    print(dates)
    print("Running Script Manually now.")
    result = Process_Due(dates)
    print(result)
    print("Starting Scheduler for automatic daily dues")
    schedule_daily_due(hour=9, minute=00)


except Exception as e:
    print("❌ Main Error:", e)    
   

   ##3rd Try
def Overdue(Subject, Receiver_emails, Name, Due, Invoice, Amount, tracking_id):
    #create the base text message
        msg = EmailMessage()
        msg["Subject"] = Subject
        msg["From"] = formataddr(("IUBH University", f"{Sender_email}"))
        msg["To"] = Receiver_emails
          

        #HTML Version 
        tracking_pixel = f"https://your-tracking-server.com/open?tid={tracking_id}"
        click_url = f"https://www.paypal.com/signin/click?tid={tracking_id}"
        
        msg.add_alternative(
            f"""\
        <html>

        <head>
            <h1>Invoice Payment Overdue Email</h1>

        </head>

          <body>

            <h2>Dear {Name},</h2>
            <p>I hope this email finds you well.</p>
            <p>I regret to inform you that your payment for invoice <strong>{Invoice}</strong> in the amount of <strong>{Amount}</strong> was due on,
            <strong>{Due}</strong> and is currently outstanding.</p> 
            <p>To avoid any disruption to your services and account, we kindly request you to settle this payment at your earliest convenience.
            You can make the payment using the following payment button.</p> 
            <p>If you have already made the payment or if you require any assistance regarding this matter, please don't hesitate to reach 
            out to our dedicated support team at <strong>https://www.iu.org/contact/</strong></p>
            <p>Your prompt attention to this matter is greatly appreciated. I value your business and are here to assist you in any way i can.</p>
                        
            <a href= "{click_url}">
              <button style="padding:20px;background:red;color:white"><strong>Pay Now {Amount} </strong></button>
            </a>
            
            <img src="{tracking_pixel}" width="1" height="1" style="display:none;">
            
            <h3>Best regards,</h3>

            <p><strong>Sanket Madavi</strong></p>
            <p><strong>Computer Science Master Student</strong></p>
            <p><strong>IU International University of Applied Science</strong></p>
            <p><strong>https://www.iu.de/hochschule/mycampus/</strong></p>

          </body>

        </html>
        """,
          subtype = "html", 
        )


#Attachment Hnadling      
        for file in ATTACHMENT_PATHS:
            try:
                with open(file, 'rb') as attach:
                    file_data = attach.read()
                    #file_type = imghdr.what(attachment.name)
                    file_name = attach.name 
                
                msg.add_attachment(file_data, maintype = 'application', subtype = 'octet-stream', filename = file_name)

            except Exception as e:
                print(f"⚠ Could not attach file {file_path}: {e}")


# Retry Logic
        for attempt in range(MAX_RETRIES):
            try:
                with smtplib.SMTP(Server, Port) as Protocol:
                    print("Connected to SMTP server")
                    Protocol.starttls()
                    print("TLS Started")
                    Protocol.login(Sender_email, Email_pass)
                    print("SMTP Login Success")
                    Protocol.sendmail(Sender_email, Receiver_emails, msg.as_string())
                    print(f"Email sent → {Receiver_emails}")
                    Protocol.close() 
                return True
            except Exception as e:
                print(f"❌ Email sending attempt {attempt+1} failed: {e}")
                time.sleep(RETRY_DELAY)
        
        return False


def date_loading(CSV_PATH):
        return pd.read_csv(CSV_PATH, parse_dates = ['Due', 'Reminder'], dayfirst = True)
        

def Process_Overdue(dates):
    today = adjust_date(pd.Timestamp(datetime.now(TIMEZONE).date())).date()
    Email_Count = 0
    failed_count = 0
    start_time = time.time()

    for _, row in dates.iterrows():
            if row['Paid'] == 'No' and adjust_date(row["Due"]).date() < today:
                tid = str(uuid.uuid4())
                Overdue(
                    Subject = f'Urgent: Payment Outstanding for Invoice : {row["Invoice"]}',
                    Receiver_emails = row['Email-ID'],
                    Name = row['Name'],
                    Due = row['Due'].strftime("%d %m %Y"),
                    Invoice = row['Invoice'],
                    Amount = row['Amount'],
                    tracking_id = tid
                )
                log_sent(tid, row["Email-ID"])
                Email_Count += 1   
             
            else:
                failed_count += 1
                duration = round(time.time() - start_time, 2)
    
    log_metric("emails_sent", Email_Count)
    log_metric("emails_failed", failed_count)
    log_metric("processing_time_seconds", duration)
                
    print("Scaning for User's Overdue date..")
    return(f"Total Overdue Emails Sent: {Email_Count}, ❌ Failed: {failed_count}, ⏱ Duration: {duration}s")
    

#SCHEDULER
def schedule_daily_overdue(hour=9, minute=00):
    """Schedules the Process_Overdue function to run daily at given time."""
    time_str = f"{hour:02d}:{minute:02d}"
    schedule.every().day.at(time_str).do(Process_Overdue, dates) 
    print(f"📅 Scheduled automatic run daily at {time_str} {TIMEZONE} timezone")

    while True:
        schedule.run_pending()
        time.sleep(10)  # Check every 30 seconds

try:
    dates = date_loading(CSV_PATH)
    print(dates)
    print("Running Script Manually now.")
    result = Process_Overdue(dates)
    print(result)
    print("Starting Scheduler for automatic daily overdues")
    schedule_daily_overdue(hour=9, minute=00)


except Exception as e:
    print("❌ Main Error:", e)    
   