# Base image
FROM python:3.9-slim

# Environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set working directory
WORKDIR /app

# Copy requirement file
COPY ./requirements/requirements.txt /app/requirements.txt
COPY ./requirements/requirements.lint.txt /app/requirements.lint.txt

# Install project dependencies
RUN pip install --upgrade pip-tools
RUN pip-sync requirements.txt requirements.lint.txt

# Copy project files
COPY . .

# Execute entrypoint.sh (collect and copy static + start gunicorn)
RUN chmod +x /app/conf/docker/entrypoint.sh
CMD ["/app/conf/docker/entrypoint.sh"]