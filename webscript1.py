from flask import Flask, render_template, request, flash
from forms import ContactForm
from flask_mail import Message, Mail


app = Flask(__name__)

app.secret_key = 'Fucku&DaHoesUCameWitandthensuckyourmotherinsideout229988'

app.config["MAIL_DEBUG"] = True
app.config["MAIL_SERVER"] = "smtp.office365.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = 'a.komolafe@outlook.com'
app.config["MAIL_PASSWORD"] = 'Adekom1993!'
 
@app.route('/contact', methods=['GET', 'POST'])
def contact():
  form = ContactForm(request.form)
 
  if request.method == 'POST':
    if form.validate() == False:
      flash('All fields are required.')
      return render_template('contact.html', form=form)
    else:
      msg = Message(form.subject.data, sender='a.komolafe@outlook.com', recipients=['a.komolafe@outlook.com'])
      msg.body = """
      From: %s &lt;%s&gt;
      %s
      """ % (form.name.data, form.email.data, form.message.data)
      
      mail.send(msg)
 
      return render_template('contact.html', success =True)
 
  elif request.method == 'GET':

    return render_template('contact.html', form=form)

mail= Mail(app)


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


if __name__ == "__main__":
    app.run(debug = True)