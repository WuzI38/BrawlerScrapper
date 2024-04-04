FROM python:3.12
WORKDIR /Brawler
ADD . /Brawler
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80
ENV PYTHONPATH /Brawler
CMD ["python", "run.py"]