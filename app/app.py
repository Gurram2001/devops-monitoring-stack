from flask import Flask
from prometheus_flask_exporter import PrometheusMetrics

app = Flask(__name__)
metrics = PrometheusMetrics(app)
@app.route('/')
def hello():
    return "Hello from DevOps on Azure VM with CI/CD! - Done by manikarthik-gurram"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
