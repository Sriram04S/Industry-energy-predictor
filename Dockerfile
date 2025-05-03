# Use official Python slim image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirement and application files
COPY requirements.txt .
COPY app.py .
COPY regression_model.pkl .
COPY .env .env

# Install Python dependencies with extended timeout
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt -i https://pypi.org/simple

# Expose the default Streamlit port
EXPOSE 8501

# Run the Streamlit app and suggest localhost in browser
CMD ["streamlit", "run", "app.py", \
     "--server.port=8501", \
     "--server.address=0.0.0.0", \
     "--browser.serverAddress=localhost"]
