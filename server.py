from flask import Flask, render_template

app = Flask(__name__)

@app.route('/', methods=['GET'])
def home():
    return render_template('index.html')

if __name__ == '__main__':
    port, debug = 5000, True
    app.run(host='0.0.0.0', port=port, debug=debug)