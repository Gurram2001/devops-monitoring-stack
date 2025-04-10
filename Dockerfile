FROM python:3.14-rc-alpine3.21
WORKDIR /app
COPY app/ /app
RUN pip install Flask
RUN pip install prometheus-flask-exporter
EXPOSE 5000
CMD ["python", "app.py"]
