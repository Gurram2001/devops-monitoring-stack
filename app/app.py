from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)

@app.route('/')
def hello():
    return "Hello from DevOps on Azure VM with CI/CD!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
