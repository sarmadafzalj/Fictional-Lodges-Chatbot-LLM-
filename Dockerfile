FROM python:3.11.4
WORKDIR /app

COPY .env /app/.env
COPY app.py /app/app.py
COPY images /app/images



RUN echo ‘nameserver 8.8.8.8’ >> /etc/resolve.conf && echo ‘nameserver 8.8.4.4’ >> /etc/resolve.conf’
#RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

ENTRYPOINT ["streamlit", "run"]
CMD ["app.py"]



