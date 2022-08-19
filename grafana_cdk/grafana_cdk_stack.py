from importlib.resources import path
from logging import root
from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam,
    aws_secretsmanager as secret,
    CfnOutput,
)
import urllib.request
from constructs import Construct
external_ip = urllib.request.urlopen('https://ident.me').read().decode('utf8')
with open("./user_data.sh") as f:
    user_data = f.read()

class GrafanaCdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #Get Vpc details
        vpc = ec2.Vpc.from_lookup(
            self,
            "VPC",
            vpc_id=self.node.try_get_context("vpc_id")
        )

        role = iam.Role(
            self,
            "Role",
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            description="This role is used to access CW logs/Metric"
        )

        role.add_managed_policy(
            policy=iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchReadOnlyAccess")
        )
        role.add_managed_policy(
            policy=iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEC2ReadOnlyAccess")
        )
        role.add_managed_policy(
            policy=iam.ManagedPolicy.from_aws_managed_policy_name("CloudWatchLogsReadOnlyAccess")
        )
        

        ami = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )

        grafana_sg = ec2.SecurityGroup(
            self,
            "GrafanaSG",
            vpc=vpc
        )

        grafana_sg.allow_all_outbound
        grafana_sg.connections.allow_from(
            ec2.Peer.ipv4(external_ip + "/32"),
            ec2.Port.tcp(22)
        )

        grafana_sg.connections.allow_from(
            ec2.Peer.ipv4(external_ip + "/32"),
            ec2.Port.tcp(3000)
        )

        grafana_pswd = secret.Secret(
            self,
            "GrafanaPswd",
            secret_name="grafana_pswd"
        )

        grafana_pswd.grant_read(role)


        grafana_instance = ec2.Instance(
            self,
            "Instance",
            vpc=vpc,
            machine_image=ami,
            instance_type=ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE2, ec2.InstanceSize.MICRO),
            instance_name="Grafana-Server",
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PUBLIC
            ),
            role=role,
            key_name=self.node.try_get_context("key_name"),
            security_group=grafana_sg,
            user_data=ec2.UserData.custom(user_data),
        )

        CfnOutput(
            self,
            "GrafanPublicIP",
            value=grafana_instance.instance_public_ip
        )