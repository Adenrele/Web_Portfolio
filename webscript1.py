from flask import Flask, render_template

app = Flask(__name__)

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

@app.route('/contact')
def contact():
    return render_template("contact.html")

if __name__ == "__main__":
    app.run(debug = True)

