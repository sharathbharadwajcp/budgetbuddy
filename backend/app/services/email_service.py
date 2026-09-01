import os
import random
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

def generate_otp_code() -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(6)])

def send_verification_email(recipient_email: str, code: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    if smtp_host and smtp_user and smtp_password:
        try:
            domain = smtp_user.split('@')[-1] if '@' in smtp_user else 'budgetbuddy.com'
            msg = MIMEMultipart('alternative')
            msg['From'] = f"BudgetBuddy <{smtp_user}>"
            msg['To'] = recipient_email
            msg['Reply-To'] = smtp_user
            msg['Subject'] = f"BudgetBuddy Security Verification Code: {code}"
            msg['Message-ID'] = f"<{code}.{int(datetime.utcnow().timestamp())}@{domain}>"
            msg['X-Priority'] = '1'
            msg['X-MSMail-Priority'] = 'High'
            msg['X-Auto-Response-Suppress'] = 'All'

            # Plain-text version
            text_body = f"""Hello,

Thank you for signing up for BudgetBuddy!

Your security verification code is: {code}

Please enter this 6-digit code in BudgetBuddy to verify your email address. This code will expire in 15 minutes.

If you did not request this verification code, no action is needed.

Best regards,
BudgetBuddy Team
"""

            # Clean, high-deliverability HTML version
            html_body = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>BudgetBuddy Verification</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f1f5f9; margin: 0; padding: 30px 10px; color: #1e293b;">
    <div style="max-width: 520px; margin: 0 auto; background-color: #ffffff; padding: 32px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);">
        <div style="text-align: center; margin-bottom: 24px;">
            <h1 style="color: #4338ca; font-size: 24px; font-weight: 700; margin: 0; tracking: -0.5px;">BudgetBuddy</h1>
            <p style="color: #64748b; font-size: 13px; margin-top: 4px;">Email Verification</p>
        </div>
        
        <p style="font-size: 14px; color: #334155; line-height: 1.6;">Hello,</p>
        <p style="font-size: 14px; color: #334155; line-height: 1.6;">Thank you for registering with BudgetBuddy. Please enter the security verification code below to activate your account:</p>
        
        <div style="text-align: center; background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 24px 0; border: 1px solid #cbd5e1;">
            <span style="font-family: 'Courier New', Courier, monospace; font-size: 32px; font-weight: 700; letter-spacing: 8px; color: #4338ca;">{code}</span>
        </div>

        <p style="font-size: 12px; color: #64748b; text-align: center; margin: 0;">This code is valid for 15 minutes.</p>
        
        <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
        
        <p style="font-size: 11px; color: #94a3b8; text-align: center; margin: 0;">If you did not request this verification email, please safely disregard it.</p>
    </div>
</body>
</html>"""

            msg.attach(MIMEText(text_body, 'plain'))
            msg.attach(MIMEText(html_body, 'html'))

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            print(f"[Email Sent] Verification OTP successfully emailed to {recipient_email}")
            return True
        except Exception as e:
            print(f"[Email Error] Failed to send email via SMTP: {e}")

    # Fallback mode
    print(f"\n=======================================================")
    print(f" [DEV EMAIL SIMULATOR] Recipient: {recipient_email}")
    print(f" [DEV EMAIL SIMULATOR] Gmail Verification Code: {code}")
    print(f"=======================================================\n")
    return True

def send_premium_request_email_to_admin(admin_email: str, student_name: str, student_email: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    subject = f"⭐ Premium Upgrade Request from {student_name}"
    text_body = f"""
Hello Administrator,

Student user {student_name} ({student_email}) has submitted a request to upgrade their BudgetBuddy account to Premium.

Please review this request in your Admin Dashboard under User Management.

Best regards,
The BudgetBuddy Team
    """

    if smtp_host and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"BudgetBuddy <{smtp_user}>"
            msg['To'] = admin_email
            msg['Subject'] = subject
            msg.attach(MIMEText(text_body, 'plain'))

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            print(f"[Email Sent] Premium upgrade request notification emailed to admin {admin_email}")
            return True
        except Exception as e:
            print(f"[Email Error] Failed to email admin via SMTP: {e}")

    print(f"\n=======================================================")
    print(f" [DEV EMAIL SIMULATOR] Admin Recipient: {admin_email}")
    print(f" [DEV EMAIL SIMULATOR] Upgrade Request from: {student_name} ({student_email})")
    print(f"=======================================================\n")
    return True

def send_premium_approval_email_to_user(recipient_email: str, student_name: str) -> bool:
    smtp_host = os.getenv("SMTP_HOST", "")
    smtp_port = int(os.getenv("SMTP_PORT", "587"))
    smtp_user = os.getenv("SMTP_USER", "")
    smtp_password = os.getenv("SMTP_PASSWORD", "")

    subject = "BudgetBuddy Premium Account Approved"
    text_body = f"""Hello {student_name},

Great news! Your request to upgrade your BudgetBuddy account to Premium has been approved by the administrator.

You now have full access to:
- 12-Month Historical Trend Charts & Multi-Year Cashflow Analytics
- 30-Day AI Predictive Cashflow & Daily Burn Rate Forecasts
- Custom Date Range Filtering
- Visual Bar & Pie Chart PDF & Excel Statement Exports

Log in now to experience your new Premium features:
http://localhost:5173/login

Best regards,
BudgetBuddy Team
"""

    if smtp_host and smtp_user and smtp_password:
        try:
            msg = MIMEMultipart('alternative')
            msg['From'] = f"BudgetBuddy <{smtp_user}>"
            msg['To'] = recipient_email
            msg['Subject'] = subject
            msg.attach(MIMEText(text_body, 'plain'))

            server = smtplib.SMTP(smtp_host, smtp_port)
            server.starttls()
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
            server.quit()
            print(f"[Email Sent] Premium approval notification emailed to {recipient_email}")
            return True
        except Exception as e:
            print(f"[Email Error] Failed to email user via SMTP: {e}")

    print(f"\n=======================================================")
    print(f" [DEV EMAIL SIMULATOR] Recipient: {recipient_email}")
    print(f" [DEV EMAIL SIMULATOR] Premium Approval for: {student_name}")
    print(f"=======================================================\n")
    return True
