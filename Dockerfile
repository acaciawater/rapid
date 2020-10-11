FROM python:3.8.2-buster
RUN export DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
	gdal-bin \
	libgdal-dev \
	zlib1g-dev \
	libjpeg-dev \
	python3-pythonmagick \
	inkscape \
	xvfb \
	poppler-utils \
	libfile-mimeinfo-perl \
	qpdf \
	libimage-exiftool-perl \
	ufraw-batch \
	ffmpeg

RUN apt-get install -y --no-install-recommends libreoffice

WORKDIR /code
COPY requirements.txt .
RUN pip install -U pip && pip install -r requirements.txt
EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
