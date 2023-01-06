import smtplib, ssl, os
import mysql.connector as mysql

from dotenv import load_dotenv
from flask import Flask, request, jsonify
from flask_cors import CORS
from template import generate_email_template
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from mysql.connector import Error
from datetime import datetime


_env = load_dotenv()
_email = os.getenv("EMAIL_ADDRESS")
_password = os.getenv("EMAIL_PASSWORD")
_port = os.getenv("EMAIL_PORT")
_interval = int(os.getenv("EMAIL_INTERVAL"))
API_PORT = os.getenv("API_PORT")

app = Flask(__name__)
CORS(app)


class Utils:
    def db_fetchone(connection, query) -> str:
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchone()

        return str(result)

    def db_fetchall(connection, query) -> list:
        cursor = connection.cursor()
        cursor.execute(query)
        result = cursor.fetchall()

        return result


@app.route("/send_mail", methods=["POST"])
def send_mail():

    try:
        connection = mysql.connect(
            host="localhost",
            user="abuyusif01",
            password="1111",
            database="dtss",
            autocommit=True,  # this will force commit after each query, eg select and update
        )

        if connection.is_connected():
            pass
    except Error as e:
        print("Error while connecting to MySQL", e)

    """this send email to the given email address"""
    data = request.get_json()
    print (data)

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

    # get last event time. since we dont wanna have alot of false positives, we email the admin only if the las event is 10mins old
    last_event = str(
        Utils.db_fetchone(
            connection=connection,
            query="select time_stamp from events where descr like '%Detected%' order by time_stamp desc limit 1;",
        )
    )[2:-3]

    """
    parse the time to datetime object, get minutes from the hour, and compare the difference
    if current time is less than 10mins old, dont send email
    """

    last_event = datetime.strptime(last_event, "%Y-%m-%d %H:%M:%S")
    current_time = datetime.strptime(_time, "%Y-%m-%d %H:%M:%S")

    interval = current_time - last_event
    interval = interval.total_seconds() / 60

    if interval > _interval:  # if the difference is greater than 10mins, send email
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
    else:
        return str("success")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=API_PORT)
