# Chọn image Python
FROM python:3.10-slim

# Tạo thư mục app
WORKDIR /app

# Copy toàn bộ file vào container
COPY . .

# Cài đặt các thư viện
RUN pip install --no-cache-dir -r requirements.txt

# Chạy bằng Gunicorn
CMD ["gunicorn", "main:app", "-b", "0.0.0.0:8080"]
