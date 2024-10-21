# Zookong Lee
# IaS Fall 2024

import os.path

from aws_cdk.aws_s3_assets import Asset as S3asset

from aws_cdk import (
    # Duration,
    Stack,
    aws_ec2 as ec2,
    aws_iam as iam
    # aws_sqs as sqs,
)

from constructs import Construct

dirname = os.path.dirname(__file__)
        
class CdkWebServerStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, cdk_lab_vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Security group for web servers
        web_server_sg = ec2.SecurityGroup(self, "WebServerSG",
            vpc=vpc,
            allow_all_outbound=True,
            description="Allow HTTP traffic",
        )
        web_server_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), "Allow HTTP traffic from anywhere")

        # Launch servers in public subnets
        public_subnet1 = vpc.public_subnets[0]
        public_subnet2 = vpc.public_subnets[1]

        web_server1 = ec2.Instance(self, "WebServer1",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=vpc,
            vpc_subnets={"subnets": [public_subnet1]},
            security_group=web_server_sg,
        )

        web_server2 = ec2.Instance(self, "WebServer2",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=vpc,
            vpc_subnets={"subnets": [public_subnet2]},
            security_group=web_server_sg,
        )

        # Security group for RDS
        rds_sg = ec2.SecurityGroup(self, "RDSSG",
            vpc=vpc,
            allow_all_outbound=True,
            description="Allow MySQL traffic from web servers",
        )
        rds_sg.add_ingress_rule(web_server_sg, ec2.Port.tcp(3306), "Allow MySQL traffic from web servers")

        # RDS instance
        rds_instance = rds.DatabaseInstance(self, "RDSInstance",
            engine=rds.DatabaseInstanceEngine.mysql(version=rds.MysqlEngineVersion.VER_8_0),
            vpc=vpc,
            vpc_subnets={"subnet_type": ec2.SubnetType.PRIVATE},
            security_groups=[rds_sg],
            allocated_storage=20,
            instance_type=ec2.InstanceType("t2.micro"),
            multi_az=False,
            publicly_accessible=False,
            database_name="MyDatabase",
            removal_policy=core.RemovalPolicy.DESTROY,  # Change to RETAIN in production
        )
