FROM python:3.12
WORKDIR /app
ADD . /app
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80
EXPOSE 3306
# CMD ["python", "run.py"]