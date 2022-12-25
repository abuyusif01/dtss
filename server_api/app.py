import smtplib, ssl, os
import random
from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from template import generate_email_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


_env = load_dotenv()
_email = os.getenv("EMAIL_ADDRESS")
_password = os.getenv("EMAIL_PASSWORD")
_port = os.getenv("EMAIL_PORT")

app = Flask(__name__)
CORS(app)


@app.route("/send_mail", methods=["POST"])
def send_mail():
    """this send email to the given email address"""
    data = request.get_json()

    try:
        _hash = data["hash"]
        _username = data["username"]
        _time = data["time"]
        _category_title = data["category_title"]
        _severity_color = data["severity_color"]
        _severity = data["severity"]
        _site_url = data["site_url"]
        _recv_email = data["recv_email"]
        _subject = data["subject"]

    except Exception as e:
        return jsonify({"status": "failed", "message": "email not sent"})

    # generate email template
    email_template = generate_email_template(
        _hash,
        _username,
        _time,
        _category_title,
        _severity_color,
        _severity,
        _site_url,
    )

    message = MIMEMultipart("alternative")
    message["Subject"] = _subject
    message["From"] = _email
    message["To"] = _recv_email

    # Turn these into plain/html MIMEText objects
    plain = MIMEText(email_template[0], "plain")
    html = MIMEText(email_template[1], "html")

    # Add HTML/plain-text parts to MIMEMultipart message
    # The email client will try to render the last part first
    message.attach(plain)
    message.attach(html)

    try:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", _port, context=context) as server:
            server.login(_email, _password)
            server.sendmail(_email, _recv_email, message.as_string())
    except Exception as e:
        print(e)
        return jsonify({"status": "failed", "message": "email not sent"})
    with open("email.html", "w") as f:
        f.write(str(email_template[1]))

    return jsonify({"status": "success", "message": "email sent successfully"})


if __name__ == "__main__":
    app.run(debug=True)
