FROM python:3.10

ENV PYTHONUNBUFFERED=1
WORKDIR /app

# Install Djano app deps
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# Copy the application and expose a test port
COPY . /app/
EXPOSE 8000

# Start the app
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]