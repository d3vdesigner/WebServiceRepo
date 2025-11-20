from flask import Flask, jsonify

app = Flask(__name__)
@app.route('/')
def hello_world():
    return 'WebService: Online!'
  
@app.route('/status')
def status_check():
    return jsonify({
        "status": "OK",
        "service": "WebServiceRepo",
        "version": "1.0"
    })
  
if __name__ == '__main__':
    app.run(debug=True, port=5000)
