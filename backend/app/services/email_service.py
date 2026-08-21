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
            msg = MIMEMultipart('alternative')
            msg['From'] = f"BudgetBuddy Support <{smtp_user}>"
            msg['To'] = recipient_email
            msg['Reply-To'] = smtp_user
            msg['Subject'] = f"{code} is your BudgetBuddy verification code"
            msg['Auto-Submitted'] = 'auto-generated'
            msg['X-Mailer'] = 'BudgetBuddy Notification System'

            # Plain-text version (Prevents Spam Filter flags)
            text_body = f"""
Hello,

Welcome to BudgetBuddy!

Your 6-digit email verification code is: {code}

This code will expire in 15 minutes. If you did not sign up for a BudgetBuddy account, please ignore this email.

Best regards,
The BudgetBuddy Team
            """

            # Clean HTML version
            html_body = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
            </head>
            <body style="font-family: Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 20px; color: #0f172a;">
                <div style="max-width: 500px; margin: 0 auto; background-color: #ffffff; padding: 30px; border-radius: 16px; border: 1px solid #e2e8f0; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                    <div style="text-align: center; margin-bottom: 24px;">
                        <h2 style="color: #4f46e5; margin: 0; font-size: 24px; font-weight: 800;">BudgetBuddy</h2>
                        <p style="color: #64748b; font-size: 13px; margin-top: 4px;">Smart Personal Finance & Expense Manager</p>
                    </div>
                    
                    <p style="font-size: 14px; color: #334155; line-height: 1.5;">Hello,</p>
                    <p style="font-size: 14px; color: #334155; line-height: 1.5;">Thank you for registering with BudgetBuddy. Please use the verification code below to complete your account setup:</p>
                    
                    <div style="text-align: center; background-color: #f1f5f9; padding: 20px; border-radius: 12px; margin: 24px 0; border: 1px border-slate-200;">
                        <span style="font-family: monospace; font-size: 32px; font-weight: 800; letter-spacing: 6px; color: #4f46e5;">{code}</span>
                    </div>

                    <p style="font-size: 12px; color: #64748b; text-align: center; margin: 0;">This code will expire in 15 minutes for security purposes.</p>
                    
                    <hr style="border: 0; border-top: 1px solid #e2e8f0; margin: 24px 0;" />
                    
                    <p style="font-size: 11px; color: #94a3b8; text-align: center; margin: 0;">If you did not request this code, please ignore this email.</p>
                </div>
            </body>
            </html>
            """

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
