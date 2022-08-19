
# Setup Grafana on EC2 using AWS-CDK!

This project creates a Grafana instance on AWS-EC2 and imports all dashboards from cloudwatch. Once deployment is complete, you can access Grafana dashboard using public IP on port 3000 to view your metrics and logs.

Set vpc_id and ssh key name on `cdk.json` that you wish to use.

To manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template using your aws-cli profile.

```
$ cdk synth --profile my-profile
```
You can check cloudformation template. Proceed if all looks okay to you.

```
$ cdk deploy --profile my-profile
```
