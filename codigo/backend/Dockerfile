FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Usuario sin privilegios; sed quita los CRLF por si el repo se clonó en Windows.
RUN sed -i 's/\r$//' entrypoint.sh && chmod +x entrypoint.sh \
    && useradd --create-home --uid 10001 app
USER app
EXPOSE 8000
ENTRYPOINT ["./entrypoint.sh"]
