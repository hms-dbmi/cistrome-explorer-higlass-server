## higlass-server docker configuration

The commands below should be run from the root directory of the higlass-server repository:

### Build the container

```sh
export S3_BUCKET_HGS="higlass-server"
export S3_BUCKET_HGS_ACCESS_KEY_ID="{your_aws_access_key_id}"
export S3_BUCKET_HGS_SECRET_ACCESS_KEY="{your_aws_secret_access_key}"
export S3_BUCKET_HGS_REGION="us-east-1"

docker build -t higlass-server -f docker-context/Dockerfile .
# TODO: move the repository under the `gehlenborglab` organization on Docker Hub.
docker tag higlass-server mkeller7/cistrome-explorer-higlass-server
```

### Run with docker-compose locally

```sh
export HGS_HOST_PORT=9000 # or =80 for production

docker-compose -f docker-context/docker-compose.yml up
```

### Push the container image to Docker Hub

```sh
# TODO: move the repository under the `gehlenborglab` organization on Docker Hub.
docker push mkeller7/cistrome-explorer-higlass-server
```

## higlass-server docker deployment to AWS ECS

### Setup

Install the [ECS CLI](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_installation.html) locally and add the `ecs-cli` to the PATH.


### Create an ECS cluster




Resources
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_Configuration.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-cli-tutorial-ec2.html