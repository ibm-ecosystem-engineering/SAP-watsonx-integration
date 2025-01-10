# Use the Red Hat UBI 8 with Python 3.11 as the base image
FROM registry.access.redhat.com/ubi8/python-311:latest

# Set environment variables for Java
ENV JAVA_HOME=/usr/lib/jvm/java-17-openjdk \
    PATH=$JAVA_HOME/bin:$PATH \
    DEBIAN_FRONTEND=noninteractive

USER 0

# Install Java 17 and other dependencies
RUN yum -y install java-17-openjdk java-17-openjdk-devel \
    gcc gcc-c++ libxslt-devel libxml2-devel curl && \
    yum clean all && \
    rm -rf /var/cache/yum

USER 1001

# Set the working directory inside the container
WORKDIR /app/backend

# Copy the requirements file to the container and install dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy your FastAPI Python script to the container
COPY app.py app.py

# Set the command to run your Python script
CMD ["python", "app.py"]
