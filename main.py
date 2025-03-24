from flask import Flask, render_template

app =Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html',title='Home',cssfile='home.css')

@app.route('/about')
def about():
    return "Hello in About Page"

@app.route("/add")
def add():
    return "Add Page"


if __name__ == '__main__':
    app.run()