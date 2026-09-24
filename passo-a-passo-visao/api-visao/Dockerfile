FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1
ENV HF_HOME = "/root/.cache/huggingface"

WORKDIR /code

COPY requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir -r /code/requirements.txt

COPY main.py /code/
EXPOSE 8081

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8081"]
