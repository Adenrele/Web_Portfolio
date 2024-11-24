from flask import Flask, render_template, request, flash,redirect, url_for
from forms import ContactForm
from flask_mail import Message, Mail
from flask_wtf.csrf import CSRFProtect
import os
from dotenv import load_dotenv
import requests
from requests_oauthlib import OAuth2Session
from similarity_program import compute_highest_similarity_from_csv 

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
app.config["MAIL_DEFAULT_SENDER"] = os.getenv("SEND_MAIL")  # Set default sender
app.config['MAIL_PASSWORD'] = os.getenv("APP_PASSWORD")  # Your password or app password
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

@app.route('/medtronic_hire_adenrele', methods=['GET', 'POST'])
def process_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part in the request.')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('No file selected.')
            return redirect(request.url)

        if file and file.filename.endswith('.csv'):
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(file_path)
            
            # Process the file
            try:
                user1, user2, similarity = compute_highest_similarity_from_csv(file_path)
                flash(f"The highest similarity is between {user1} and {user2} with a cosine similarity score of {similarity:.4f}")
            except Exception as e:
                flash(f"An error occurred while processing the file: {e}")
            
            # Delete the file after processing
            try:
                os.remove(file_path)
                flash('File deleted after processing.')
            except Exception as e:
                flash(f"An error occurred while deleting the file: {e}")
            
            
            return redirect(request.url)
        else:
            flash('Invalid file type. Please upload a CSV file.')
            return redirect(request.url)
    
    return render_template("job.html")  
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=3000)
