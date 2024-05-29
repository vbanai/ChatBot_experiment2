mkdir -p /opt && chmod -R 777 /opt
gunicorn --bind=0.0.0.0 --timeout 600 --chdir . main:app
