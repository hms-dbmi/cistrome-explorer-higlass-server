## higlass-server docker configuration

The commands below should be run from the root directory of the higlass-server repository:

### Build the container

```sh
docker build -t higlass-server -f docker-context/Dockerfile .
# TODO: move the repository under the `gehlenborglab` organization on Docker Hub.
docker tag higlass-server mkeller7/cistrome-explorer-higlass-server
```

### Run with docker-compose locally

Before running the `docker-compose` command, set the required configuration environment variables.
The AWS credentials with the `S3_BUCKET_` prefix should be associated with an IAM user that has `List` and `Read` privileges for the `$S3_BUCKET_HGS` bucket.

```sh
export HGS_HOST_PORT=9000 # or =80 for production

export S3_BUCKET_HGS="higlass-server"
export S3_BUCKET_HGS_ACCESS_KEY_ID="{your_aws_access_key_id}"
export S3_BUCKET_HGS_SECRET_ACCESS_KEY="{your_aws_secret_access_key}"
export S3_BUCKET_HGS_REGION="us-east-1"

docker-compose -f docker-context/docker-compose.yml up
```

### Push the container image to Docker Hub

```sh
# TODO: move the repository under the `gehlenborglab` organization on Docker Hub.
docker push mkeller7/cistrome-explorer-higlass-server
```

## higlass-server docker deployment to AWS ECS

### Setup

Install the [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/install-cliv2-linux.html) locally and add `aws` to the PATH.
Install the [ECS CLI](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_installation.html) locally and add `ecs-cli` to the PATH.


### Create an ECS cluster

The AWS credentials with the `S3_BUCKET_HGS` prefix should be associated with an IAM user that has `List` and `Read` privileges for the `$S3_BUCKET_HGS` bucket.
The AWS credentials with the `ECS_PROFILE_HGS` prefix should be associated with an IAM user that has the policies `AmazonECS_FullAccess`, `AmazonEC2FullAccess`, `AmazonEC2RoleforSSM`, and `IAMFullAccess`.

```sh
# Set the S3 bucket credentials.
export S3_BUCKET_HGS="higlass-server"
export S3_BUCKET_HGS_ACCESS_KEY_ID="{your_aws_access_key_id}"
export S3_BUCKET_HGS_SECRET_ACCESS_KEY="{your_aws_secret_access_key}"
export S3_BUCKET_HGS_REGION="us-east-1"

# Set the ECS credentials.
export ECS_CLUSTER_HGS="higlass-server"
export ECS_PROFILE_HGS="higlass-server"
export ECS_PROFILE_HGS_ACCESS_KEY_ID="{your_aws_access_key_id}"
export ECS_PROFILE_HGS_SECRET_ACCESS_KEY="{your_aws_secret_access_key}"
export ECS_HGS_REGION="us-east-1"

# Prepare to create a key pair.
export ECS_HGS_KEY_NAME="higlass_server_ecs"
mkdir -p ~/aws

# Set the default environment variables for the aws cli.
export AWS_ACCESS_KEY_ID=$ECS_PROFILE_HGS_ACCESS_KEY_ID
export AWS_SECRET_ACCESS_KEY=$ECS_PROFILE_HGS_SECRET_ACCESS_KEY
export AWS_DEFAULT_REGION=$ECS_HGS_REGION

# Create a key pair.
aws ec2 create-key-pair --key-name $ECS_HGS_KEY_NAME > ~/aws/$ECS_HGS_KEY_NAME.pem

# Create a cluster configuration.
ecs-cli configure \
    --cluster $ECS_CLUSTER_HGS \
    --default-launch-type EC2 \
    --config-name $ECS_CLUSTER_HGS \
    --region $ECS_HGS_REGION

# Create a profile configuration.
ecs-cli configure profile \
    --profile-name $ECS_PROFILE_HGS \
    --access-key $ECS_PROFILE_HGS_ACCESS_KEY_ID \
    --secret-key $ECS_PROFILE_HGS_SECRET_ACCESS_KEY

# Create a cluster.
ecs-cli up \
    --cluster-config $ECS_CLUSTER_HGS \
    --ecs-profile $ECS_PROFILE_HGS \
    --keypair $ECS_HGS_KEY_NAME \
    --capability-iam \
    --size 1 \
    --instance-type t2.medium
    
# Deploy the Compose File to the cluster.
export HGS_HOST_PORT=80
ecs-cli compose \
    --project-name higlass-server \
    --file docker-context/docker-compose.yml \
    up \
    --cluster-config $ECS_CLUSTER_HGS \
    --ecs-profile $ECS_PROFILE_HGS

```

Resources
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_Configuration.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-cli-tutorial-ec2.html