FROM python:3.9
WORKDIR /app
COPY . /app
RUN ["pip", "install", "-U", "pipenv"]
RUN ["pipenv", "install"]
EXPOSE 8000
CMD ["pipenv", "run", "uvicorn", "--host", "0.0.0.0", "--port", "8000", "app:app", "--log-level", "trace"]
