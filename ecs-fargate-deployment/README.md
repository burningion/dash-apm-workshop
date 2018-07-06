# Agent ECS Fargate Deployment (WIP)

**THIS IS A WORK IN PROGRESS, AS A POTENTIAL BONUS TO THE WORKSHOP, DEPLOYING AN AGENT IN ECS / FARGATE**

This tutorial assumes you've never set up a cluster on ECS Fargate before.

First, we need to install the AWS cli and the ECS cli.

Once that's done, we'll need to create a task execution IAM role. The `task-execution-assume-role.json` file in this directory has the permissions in it. To apply it, `cd` into this directory and run the following:

```bash
$ aws iam --region us-east-2 create-role --role-name ecsTaskExecutionRole --assume-role-policy-document file://task-execution-assume-role.json
$ aws iam --region us-east-2 attach-role-policy --role-name ecsTaskExecutionRole --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
```

This creates the role, and then attaches the policy.

Next, we'll configure the cluster itself from the ECS cli.

In the same directory, run:

```bash
$ ecs-cli configure --cluster apm-workshop --region us-east-2 --default-launch-type FARGATE --config-name apm-workshop
INFO[0000] Saved ECS CLI cluster configuration apm-workshop.
$ ecs-cli configure profile --access-key <youraccesskey> --secret-key <yoursecretkey> --profile-name apm-workshop
INFO[0000] Saved ECS CLI profile configuration apm-workshop.
```

Finally, we'll spin up the cluster and add a security group using the vpc name from `ecs-cli up`. We'll then open port 5000 to the world, so we can see our application:

```bash
$ ecs-cli up
INFO[0000] Created cluster                               cluster=apm-workshop region=us-east-2
INFO[0001] Waiting for your cluster resources to be created... 
INFO[0001] Cloudformation stack status                   stackStatus=CREATE_IN_PROGRESS
VPC created: vpc-<YOURVPC>
Subnet created: subnet-<YOURSUBNET>
Subnet created: subnet-<YOUROTHERSUBNET>
Cluster creation succeeded.
$ aws ec2 create-security-group --group-name "my-sg" --description "My security group" --vpc-id "vpc-<YOURVPC>"
{
    "GroupId": "<YOURSECURITYGROUPID>"
}
$ aws ec2 authorize-security-group-ingress --group-id "<YOURSECURITYGROUPID>" --protocol tcp --port 5000 --cidr 0.0.0.0/0
```

We're now ready to deploy with a docker-compose file.

Unfortunately, our `${STEP}` environment variable strings used in the walkthrough will generate a segfault in the ecs-cli, so in this directory we've just manually set them to be `step05`.

Besides this, in a real world environment we won't be setting an agent image. Instead, we'll create a `DAEMON` service for our Datadog agent, that runs on every active container image to ship traces back to Datadog. So we've also removed the agent image from the new `docker-compose.yml`:

```yaml
version: '3'
services:
  redis:
    image: "redis:4.0.10-alpine"
  web:
    environment:
      - FLASK_APP=api.py
      - FLASK_DEBUG=1
    build: .
    command: flask run --port=5000 --host=0.0.0.0
    ports:
      - "5000:5000"
    volumes:
      - "./step0${STEP}:/app"
    depends_on:
      - agent
      - redis
      - thinker
  thinker:
    environment:
    - FLASK_APP=thinker.py
    - FLASK_DEBUG=1
    build: .
    command: flask run --port=5001 --host=0.0.0.0
    ports:
      - "5001:5001"
    volumes:
      - "./step0${STEP}:/app"
    depends_on:
      - agent
      - redis
```

Finally, AWS doesn't support locally built images, (our `build: .` line that uses our Dockerfile), or our host `volumes`, so we'll need to ship our built images from the workshop to Amazon. We should probably also disable debugging in production.

But first, lets get a Docker login to push images using the aws cli:

```bash
$ aws ecr get-login --no-include-email
```

This will output a docker login command for you to copy and paste directly into the command line. It will log you in to the Amazon ECR registry with Docker.

We can then create a repository to push to using the aws cli:

```bash
$ aws ecr create-repository --repository-name dash-workshop/flask-app
{
    "repository": {
        "repositoryArn": "arn:aws:ecr:us-east-2:<YOURIDGOESHERE>:repository/dash-workshop/flask-app",
        "repositoryUri": "<YOURIDGOESHERE>.dkr.ecr.us-east-2.amazonaws.com/dash-workshop/flask-app",
        "createdAt": 1530912888.0,
        "repositoryName": "dash-workshop/flask-app",
        "registryId": "<YOURIDGOESHERE>"
    }
}
```

Next, we can do a `docker images`, and get a list of our images we've created:

```bash
$ docker images
REPOSITORY                                      TAG                                       IMAGE ID            CREATED             SIZE
dashapmworkshop_thinker                         latest                                    4080b18ca467        3 days ago          116MB
dashapmworkshop_web                             latest                                    4080b18ca467        3 days ago          116MB
```

Both of these were from the workshop, and built with host volumes. We'll need copy the final files in a docker image, and rebuild it.

Our original `Dockerfile` becomes:

```yaml
FROM python:3.6.2-alpine3.6
LABEL maintainer="Datadog Inc. <manu@datadoghq.com>"

COPY requirements.txt /app/requirements.txt
COPY ./step05 /app
WORKDIR /app
RUN pip install -r requirements.txt
```

Just one more thing, we need to change our API call to be requesting `localhost:5001`, as we haven't set up real networking on our ECS instance. The code in this directory already handles that.

Finally, let's build, tag and push our images using docker:

```bash
$ docker build -t apm-workshop .
Successfully built 16becd01a280
Successfully tagged apm-workshop:latest
$ docker tag 16becd01a280 <YOURIDHERE>.dkr.ecr.us-east-2.amazonaws.com/dash-workshop/flask-app
$ docker push <YOURIDHERE>.dkr.ecr.us-east-2.amazonaws.com/dash-workshop/flask-app
```

And that's it! We can now add our repositories to the `docker-compose.yml`, and push!

```yaml
version: '3'
services:
  redis:
    image: "redis:4.0.10-alpine"
  web:
    image: "<yourrepositoryimagegoeshere>"
    environment:
      - FLASK_APP=api.py
    command: flask run --port=80 --host=0.0.0.0
    ports:
      - "80:80"
    depends_on:
      - agent
      - redis
      - thinker
  thinker:
    image: "<yourrepositoryimagegoeshere>"
    environment:
    - FLASK_APP=thinker.py
    command: flask run --port=5001 --host=0.0.0.0
    ports:
      - "5001:5001"
    depends_on:
      - agent
      - redis
```

Bring it all up from the command line:

```bash
$ ecs-cli compose --project-name apm-workshop service up --cluster-config apm-workshop
```

To stop our containers, we just:


```bash
$ ecs-cli compose --project-name apm-workshop service stop --cluster-config apm-workshop
```
