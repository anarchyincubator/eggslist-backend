# Pull official base image
FROM python:3.9.6-alpine
# Set up work directory
WORKDIR /usr/src/app
RUN mkdir /usr/src/tmp
# Install required unix libraries
RUN apk add zlib-dev jpeg-dev gcc musl-dev
# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
# Install dependencies
RUN python -m pip install -U --force-reinstall pip
COPY ./requirements.txt .
RUN pip install -r requirements.txt
# Process Entrypoint
COPY ./entrypoint.sh .
RUN sed -i 's/\r$//g' /usr/src/app/entrypoint.sh
RUN chmod +x /usr/src/app/entrypoint.sh
# Copy project
COPY . .
# Run Entrypoint script
ENTRYPOINT ["./entrypoint.sh"]
