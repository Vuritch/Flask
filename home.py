from flask import Flask ,render_template



app =Flask(__name__)   #naming the appplakash


@app.route('/')
def index():

    return render_template("home.html",pagetitle="Home page")


@app.route('/about')
def about():
    return render_template("about.html",pagetitle="Abdout us")

@app.route('/add')
def add():
    return render_template("add.html",pagetitle="add page")



if __name__ == "__main__":    #functions will run only if i run only this file if import this file in another file it will not run
    app.run(debug=True,port=9000)