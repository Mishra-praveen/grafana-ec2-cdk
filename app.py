#!/usr/bin/env python3
import os

import aws_cdk as cdk

from grafana_cdk.grafana_cdk_stack import GrafanaCdkStack


app = cdk.App()
env=cdk.Environment(account='123456789012', region='us-east-1')
GrafanaCdkStack(app, "GrafanaCdkStack", env=env)

app.synth()
