# ZAAI Infrastructure

This repository contains everything to build the Airflow used by the Data Team to schedule, run and monitor all tasks to serve the needs of the stakeholders.

##### Local Requirements
To run everything locally you need the following:
 - docker (with 4-6 GB of memory in Rescources)
 - python virtual environment (requires virtualenv or similar to select a python version different from the system default)
    - python 3.10
    - pip version 20.2.4 (less than 20.3.)


## LOCAL SETUP
Please download both folders (infrastructure and mlflow)
Inside each folder, you have a readme to run each container


After having both containers up, you should verify that everything is connected.

## Default logins:

### Airflow Webserver : 
- User: Admin
- Password: admin

### pgAdmin :

- PGADMIN_DEFAULT_EMAIL=admin@admin.com
- PGADMIN_DEFAULT_PASSWORD=root

### Minio UI:

- MINIO_ROOT_USER=zaai_infrastructure
- MINIO_ROOT_PASSWORD=zaai_infrastructure

### MLflow:

- AWS_ACCESS_KEY_ID=mlflow
- AWS_SECRET_ACCESS_KEY=mlflow_pwd



If pgAdmin is not displaying any server, register to a server doing the following: 

![pgsetup](https://github.com/zaai-ai/infrastructure/assets/106923001/c5e5dbcc-bea4-4fc2-9fb9-9da118c3e66c)

