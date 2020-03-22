FROM python:3.8

EXPOSE 5000

# Install JDK for Lucene
RUN apt-get update && apt-get install -y default-jdk ant
WORKDIR /usr/lib/jvm/default-java/jre/lib
RUN ln -s ../../lib amd64

# Install Lucene
WORKDIR /usr/src/pylucene
RUN curl http://apache.uvigo.es/lucene/pylucene/pylucene-8.1.1-src.tar.gz | tar -xz --strip-components=1
RUN cd jcc && NO_SHARED=1 JCC_JDK=/usr/lib/jvm/default-java python setup.py install
RUN make all install JCC='python -m jcc' ANT=ant PYTHON=python NUM_FILES=8

# Keeps Python from generating .pyc files in the container
ENV PYTHONDONTWRITEBYTECODE 1

# Turns off buffering for easier container logging
ENV PYTHONUNBUFFERED 1

# Install pip requirements
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
EXPOSE 5000

CMD ["gunicorn", "--timeout", "3600", "--bind", "0.0.0.0:5000", "app:app"]
