# pull official base image
FROM python:3.12.12-slim-trixie

# set work directory
WORKDIR /usr/src

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# install system dependencies
RUN apt-get update && apt-get install -y netcat-traditional && rm -rf /var/lib/apt/lists/*
# install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt

# copy project
COPY . .


# # copy entrypoint.sh
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/entrypoint.sh
RUN chmod +x /usr/src/entrypoint.sh

# # run entrypoint.sh
ENTRYPOINT ["/usr/src/entrypoint.sh"]