FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PORT=3010

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY src ./src
COPY app ./app
COPY data/raw ./data/raw
COPY models ./models

# Use the committed model. Train only if it is missing (training needs ~1 GB RAM).
# Then load it once so an incompatible model fails the build instead of the live app.
RUN if [ ! -f models/pipeline.joblib ]; then OMP_NUM_THREADS=1 python -m src.train; fi \
 && python -c "from src.predict import SegmentPredictor; SegmentPredictor(); print('model OK')"

RUN useradd --create-home --uid 1000 appuser && chown -R appuser /app
USER appuser

EXPOSE 3010

HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD ["python", "-c", "import os, urllib.request; urllib.request.urlopen('http://127.0.0.1:%s/health' % os.environ.get('PORT', '3010'), timeout=4)"]

CMD ["sh", "-c", "exec gunicorn --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY:-2} --threads 4 --timeout 60 --access-logfile - app.app:app"]
