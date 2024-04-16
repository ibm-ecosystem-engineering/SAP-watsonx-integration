FROM python:3.10.13-slim
ENV LANG C.UTF-8

# PYTHONUNBUFFERED keeps Python from buffering stdout, and delivers logs more quickly.
# PYTHONDONTWRITEBYTECODE keeps Python from writing .pyc files that are unnecessary in this case.
ENV PYTHONUNBUFFERED=TRUE \
    PYTHONDONTWRITEBYTECODE=TRUE

RUN mkdir -p /app/src
WORKDIR /app/src

COPY requirements.txt requirements.txt
COPY auto.py auto.py
COPY scikit_model.pkl scikit_model.pkl

# There's substantial overlap between scipy and numpy that we eliminate by linking them together.
# Likewise, pip leaves the install caches populated which uses a significant amount of space.
# These optimizations save a fair amount of space in the image, which reduces start up time.
RUN pip install --upgrade pip distlib
RUN pip install --no-cache-dir -r requirements.txt

# Required to execute script
RUN chgrp -R nogroup /app && \
    chmod -R 770 /app
    
EXPOSE 7000

CMD ["/bin/sh", "-c", "set -e && echo \"Starting\" && gunicorn --chdir /app/src auto:app -b 0.0.0.0:7000"]

