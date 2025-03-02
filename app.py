from flask import Flask,render_template 
hotel_app=Flask(__name__)
@hotel_app.route('/')
def Home():
    return render_template("homepage.html")
@hotel_app.route('/about')
def about():
    return render_template("about.html")


if __name__ == "__main__":
     hotel_app.run(debug=True,port=9000)