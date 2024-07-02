#### How to run Mlflow:

Note :
Please execute the following commands in this directory.
If you are using Docker desktop, it should be running.

```bash
# Build the image (Use this command first)
docker compose -f docker-compose.yml build 

# Run the containers in the `detached` mode (Use this command after you build the image)
docker compose -f docker-compose.yml up -d

# Shut down (Use this command to shut down the container)
docker compose -f docker-compose.yml down
```
