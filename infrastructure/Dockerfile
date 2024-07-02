FROM apache/airflow:2.5.2-python3.10

USER root
# Add repo definition for odbc
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
RUN curl https://packages.microsoft.com/config/debian/10/prod.list > /etc/apt/sources.list.d/mssql-release.list
RUN curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list

RUN apt-get update && ACCEPT_EULA=Y apt-get install -y libgomp1 gcc msodbcsql18 mssql-tools18
ENV PATH="$PATH:/opt/mssql-tools18/bin"
RUN apt-get install -y unixodbc-dev libgssapi-krb5-2

USER airflow

COPY requirements/base.txt $AIRFLOW_HOME/base.txt

# Install the requirements file
RUN pip install --upgrade pip==23.3.1
RUN pip install --upgrade pyopenssl==22.1.0
RUN pip install "apache-airflow==${AIRFLOW_VERSION}" -r base.txt

COPY airflow.cfg $AIRFLOW_HOME/airflow.cfg
COPY webserver_config.py $AIRFLOW_HOME/webserver_config.py
