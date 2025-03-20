FROM python:3.13.2-slim
WORKDIR /app
COPY meowmaker.py .
COPY whiskers .
RUN chmod +x ./whiskers
RUN mkdir -p /workspace
RUN echo "deb https://deb.debian.org/debian trixie main contrib" > /etc/apt/sources.list
RUN echo "" > /etc/apt/sources.list.d/debian.sources
RUN apt-get update && apt-get full-upgrade -y && apt-get clean && apt-get autoremove -y
CMD ["python", "/app/meowmaker.py"]