```sh
# from the root directory of the higlass-server repository:

export REDIS_PASS={some_redis_password}
export S3_BUCKET_HGS="higlass-server"
export S3_BUCKET_HGS_ACCESS_KEY_ID={your_aws_access_key_id}
export S3_BUCKET_HGS_SECRET_ACCESS_KEY={your_aws_secret_access_key}
export S3_BUCKET_HGS_REGION="us-east-1"

docker build -t higlass-server -f docker-context/Dockerfile .
docker-compose -f docker-compose.yml up
```

Resources
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ECS_CLI_Configuration.html
- https://docs.aws.amazon.com/AmazonECS/latest/developerguide/ecs-cli-tutorial-ec2.html