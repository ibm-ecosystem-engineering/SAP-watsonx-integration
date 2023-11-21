FROM python:3.10.12
ENV LANG C.UTF-8

# There's substantial overlap between scipy and numpy that we eliminate by linking them together.
# Likewise, pip leaves the install caches populated which uses a significant amount of space.
# These optimizations save a fair amount of space in the image, which reduces start up time.
RUN pip3 install --upgrade pip distlib
RUN pip3 --no-cache-dir install \
    numpy scipy pandas flask gunicorn \
    scikit-learn==1.1.1 \
    ibm-cloud-sdk-core==3.16.5 ibm_watson_openscale==3.0.32 autoai-libs==1.14.6 python-dotenv

# PYTHONUNBUFFERED keeps Python from buffering our standard output stream,
# which means that logs can be delivered to the user quickly.
ENV PYTHONUNBUFFERED=TRUE

# PYTHONDONTWRITEBYTECODE keeps Python from writing .pyc files that are unnecessary in this case.
ENV PYTHONDONTWRITEBYTECODE=TRUE

RUN mkdir -p /app/src
COPY auto.py /app/src/auto.py
COPY scikit_model.pkl /app/src/scikit_model.pkl

ADD auto.py auto.py
ADD scikit_model.pkl scikit_model.pkl

# Required to execute script
RUN chgrp -R nogroup /app && \
    chmod -R 770 /app
    
EXPOSE 7000

#CMD ["python", "auto.py"]

