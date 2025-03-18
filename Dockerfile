FROM python:3.13.2 AS backend-builder
WORKDIR /app
COPY requirements.txt .
RUN apt update && apt install -y --no-install-recommends build-essential
RUN pip install --no-cache-dir -r requirements.txt
FROM python:3.13.2-slim
WORKDIR /app
COPY --from=backend-builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY meowmaker.py .
COPY whiskers .
RUN chmod +x ./whiskers
RUN echo "deb https://deb.debian.org/debian trixie main contrib" > /etc/apt/sources.list
RUN echo "" > /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get full-upgrade -y && apt-get clean && apt-get autoremove -y
CMD ["python", "/app/meowmaker.py"]