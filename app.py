from flask import Flask, render_template, request
app = Flask(__name__)
@app.route("/")
def index():
    return render_template('index.html')
@app.route("/add", methods=["POST"])
def add():
    data = request.form.get("data")
    print(data)
    return "success"

if __name__ == "__main__":
    app.run(debug=True)