FROM python:3.10.9

ENV PYTHONUNBUFFERED 1

# Create directory structure
RUN mkdir -p /app/backend
WORKDIR /app/backend

# Copy just the requirements file
COPY requirements.txt /app/backend/

# Install dependencies
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the rest of the application code
COPY . /app/backend/

# Collect static files
#RUN python manage.py collectstatic --noinput

# Expose the port
EXPOSE 8000

# Run migrations
#CMD ["python", "manage.py", "migrate"]
