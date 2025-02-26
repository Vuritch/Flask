# Import the necessary classes and functions from Flask
from flask import Flask, render_template

# Create an instance of the Flask application
app = Flask(__name__)

# Define the route for the homepage ("/")
@app.route("/") 
def homepage():
    # Render the 'index.html' template and pass variables like title and CSS
    return render_template("index.html", title="Home", css="main.css")

# Define the route for the about page ("/about")
@app.route("/about")  
def about():
    # Render the 'about.html' template and pass variables like title and CSS
    return render_template("about.html", title="About", css='master.css')

# Check if the script is being run directly
if __name__ == "__main__":
    # Run the Flask app with debug mode enabled on port 9000
    app.run(debug=True, port=9000)
