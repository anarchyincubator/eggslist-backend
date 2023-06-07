# Pull official base image
FROM python:3.9-slim-buster as builder
# Set up work directory
WORKDIR /usr/src/app
RUN mkdir /usr/src/tmp
# Install required unix libraries
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Install dependencies
RUN python -m pip install -U --force-reinstall pip
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

# Process Entrypoint
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
# Copy project

FROM python:3.9-slim-buster as main
# create the app user
# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

# install dependencies
RUN apt-get update &&\
	yes | apt-get install binutils libproj-dev gdal-bin python-gdal python3-gdal

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --no-cache /wheels/*

# Copy Project
COPY . $APP_HOME
RUN sed -i 's/\r$//g' $APP_HOME/entrypoint.sh
RUN chmod +x $APP_HOME/entrypoint.sh
RUN --mount=type=secret,id=ENV_SECRETS cat /run/secrets/ENV_SECRETS | base64 -d >> $APP_HOME/.env

#RUN chown -R app:app $APP_HOME

#USER app

#COPY . .
# Run Entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
