FROM python:3

ENV PYTHONUNBUFFERED=1
WORKDIR /code

COPY translations /translations
COPY requirements /code/requirements
COPY back /code/

RUN pip install -r requirements/prod.txt

COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/docker-entrypoint.sh"]
CMD ["back"]
