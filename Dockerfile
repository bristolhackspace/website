FROM docker.io/python:3.11.8

RUN mkdir /website

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
EXPOSE 8080
ENV PYTHONUNBUFFERED=TRUE
CMD ["gunicorn", "--enable-stdio-inheritance", "-w", "2", "-b", "unix:/website/hackspace_website.sock", "hackspace_website:create_app()"]
