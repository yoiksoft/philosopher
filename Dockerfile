FROM python:3.9
WORKDIR /app

ENV VIRTUAL_ENV=/opt/venv
RUN python3 -m venv $VIRTUAL_ENV
ENV PATH="$VIRTUAL_ENV/bin:$PATH"

ARG REQUIREMENTS_TXT=requirements.txt
COPY $REQUIREMENTS_TXT
RUN pip install -r $REQUIREMENTS_TXT

COPY . /app

EXPOSE 8000
CMD ["python", "-m", "uvicorn", "--host", "0.0.0.0", "--port", "8000", "app:app", "--log-level", "trace"]
