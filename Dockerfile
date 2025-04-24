# app/Dockerfile

FROM python:3.12-slim

WORKDIR /

RUN apt-get update && apt-get install -y \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY . .

RUN pip3 install -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run", "🗨️Shadow_Insights.py", "--server.port=8501", "--server.address=0.0.0.0"]