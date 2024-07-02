

#### Initialize the database
Use this command to initialize the database, before building the container
```
docker compose -f docker-compose.yml run webserver airflow db init
```

To apply DB Migrations, run:
```
docker compose -f docker-compose.yml run webserver airflow db upgrade
```

To reset the DB (**this deletes all your data in that db**), run:
```
docker compose -f docker-compose.yml run webserver airflow db reset
```

#### How to create an Admin User
```bash
docker compose -f docker-compose.yml run webserver airflow users create --username admin --firstname admin --lastname admin --role Admin --email admin@admin.com --password admin
```

#### How to run airflow locally
```bash
# Build the image - Use the following command first
docker compose -f docker-compose.yml build

# Run the containers in the `detached` mode - Use this command after you build the container
docker compose -f docker-compose.yml up -d

# Shut down
docker compose -f docker-compose.yml down
```

#### How to make Dags Available
The `docker-compose.yml` file takes environment variables for all Dag repositories. All environment variables are absolute paths on your local machine.

Add the environment variables to `.bashrc` or `.zshrc` file, example for Dags in `dag` folder:

`export DAG_DIRECTORY=/Users/rafael/Documents/infrastructure/infrastructure/dags`
