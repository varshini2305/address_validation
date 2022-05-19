#define Dockerfile, image, container

FROM python:3.9.7
ADD Monkey_Type_Detection.py .
COPY current_requirements.txt .
RUN pip install --upgrade pip
# RUN pip install pywin32==301
RUN pip install -r current_requirements.txt
CMD ["python","./Monkey_Type_Detection.py"]
