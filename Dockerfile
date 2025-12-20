# syntax=docker/dockerfile:1

FROM python:latest
# WORKDIR /app
COPY . .
# RUN apt-get update && apt-get install -y python3.11 python3-pip
ENV PIP_ROOT_USER_ACTION=ignore
RUN pip install -r requirements.txt
ENV FLASK_APP hackspace_website:create_app
ENV FLASK_ENV development
EXPOSE 5000
CMD ["flask"]
#ENTRYPOINT ["flask run"]

