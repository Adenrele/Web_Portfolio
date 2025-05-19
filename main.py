from flask import Flask, render_template, request, flash,redirect, url_for, session
from forms import ContactForm, FlaskForm
from flask_mail import Message, Mail
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv
import requests
from requests_oauthlib import OAuth2Session
from QR_code import QRCreator

UPLOAD_FOLDER = 'uploads'  # Folder where uploaded files will be stored
os.makedirs(UPLOAD_FOLDER, exist_ok=True)  # Ensure the folder exists


# Load the .env file
load_dotenv()

# OAuth2 credentials
CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
REFRESH_TOKEN = os.getenv("GOOGLE_REFRESH_TOKEN")
TOKEN_URL = 'https://oauth2.googleapis.com/token'

# Flask configuration
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv("app_secret_key")

# Set mail configuration
app.config["MAIL_SERVER"] = os.getenv("mailserver")
app.config["MAIL_PORT"] = os.getenv("mailport")
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = os.getenv("SEND_MAIL")
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("SEND_MAIL")  
app.config['MAIL_PASSWORD'] = os.getenv("APP_PASSWORD") 
receivemail = os.getenv("receivemail")

mail = Mail(app)

# Function to get new access token
def get_access_token():
    token_data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'refresh_token': REFRESH_TOKEN,
        'grant_type': 'refresh_token',
    }

    response = requests.post(TOKEN_URL, data=token_data)
    response_json = response.json()
    return response_json['access_token']


# Update MAIL_PASSWORD dynamically with access token
def update_mail_password():
    app.config["MAIL_PASSWORD"] = get_access_token()

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    form = ContactForm(request.form)

    if request.method == 'POST':
     

        # Validate form
        if form.validate() == False:
           
            flash('All fields are required.')
            return render_template('contact.html', form=form)
        else:
          
            update_mail_password()  # Get a fresh access token

            # Check if the access token is valid
            access_token = app.config.get("MAIL_PASSWORD")  # Assuming MAIL_PASSWORD is set to access token
        

            # Prepare and send the email
            msg = Message(form.subject.data, sender=os.getenv("SEND_MAIL"), recipients=[receivemail])
            msg.body = """
            From: %s <%s>
            %s
            """ % (form.name.data, form.email.data, form.message.data)

            try:
                mail.send(msg)
                flash('Your message has been sent successfully!', 'success')
            except Exception as e:
              
                flash('Failed to send the message. Try again later.', 'danger')

            return render_template('contact.html', success=True)

    elif request.method == 'GET':
        return render_template('contact.html', form=form)

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/cv')
def cv():
    return render_template("cv.html")

@app.route('/projects')
def projects():
    return render_template("projects.html")

@app.route('/blogs')
def blogs():
    return render_template("blogs.html")

@app.route('/qrcode', methods=["GET", "POST"])
def qrcode():
    success = False
    file_name = None

    if request.method == "POST":
        url = request.form.get("url")
        if url:
            file_name_base = "qr_image"
            file_type = "png"  # default file type

            qr = QRCreator(url=url, file_name=file_name_base, file_type=file_type)
            qr_image = qr.create_qr_code()
            file_name = qr.save_qr(qr_image)
            success = True

    return render_template("QR.html", success=success, file_name=file_name)

@app.route('/clear_qr', methods=["POST"])
def clear_qr():
    """Deletes the QR code image from the file system."""
    # Retrieve the filename from the session.
    file_name = session.pop('qr_file_name', None) # use the key 'qr_file_name'
    if file_name:
        #  Use the QRCreator to get the file path.
        qr_creator = QRCreator(url="") #  Need to instantiate, even without URL.
        file_path = qr_creator.get_file_path(file_name)
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")  # Add logging
            else:
                print(f"File not found: {file_path}") # Add logging
        except Exception as e:
            print(f"Error deleting file: {e}")
            return "Error deleting file", 500  # Return an error response
    return '', 204 #  No content, success


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
