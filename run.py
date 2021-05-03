from flask import Flask

app = Flask(__name__)

@app.route("/metrics")
def metric():
    return "1"

if __name__ == '__main__':
    app.run(debug=True)