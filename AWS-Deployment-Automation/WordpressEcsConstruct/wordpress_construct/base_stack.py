import json
from aws_cdk import (
    core,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_efs as efs
)

cpvCIDR = "10.2.0.0/16"
efs_removal_policy = "SNAPSHOT" #RETAIN
efs_lifecycle_policy = efs.LifecyclePolicy.AFTER_7_DAYS # https://docs.aws.amazon.com/efs/latest/ug/lifecycle-management-efs.html
efs_automatic_backups = True

class WordpressBaseConstructStack(core.Stack):

    def getDBEngine(self,engine):
        if(engine == 'MYSQL'):
            return rds.DatabaseInstanceEngine.MYSQL
        
    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Example automatically generated. See https://github.com/aws/jsii/issues/826
        vpc = ec2.Vpc(self, "vpc",
            cidr=cpvCIDR,
            max_azs=3,
            subnet_configuration=[
                {
                    'cidrMask': 28,
                    'name': 'public',
                    'subnetType': ec2.SubnetType.PUBLIC
                },
                {
                    'cidrMask': 28,
                    'name': 'private',
                    'subnetType': ec2.SubnetType.PRIVATE
                },
                {
                    'cidrMask': 28,
                    'name': 'db',
                    'subnetType': ec2.SubnetType.ISOLATED
                }
            ]
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_rds/DatabaseCluster.html
        ##TODO:ADD Aurora Serverless Option
        rds_instance = rds.DatabaseCluster(self,'wordpress-db',
            engine=rds.DatabaseClusterEngine.aurora_mysql(
                version=rds.AuroraMysqlEngineVersion.VER_2_07_2
            ),
            instance_props=rds.InstanceProps(
                vpc=vpc
            )
        )

        EcsToRdsSeurityGroup= ec2.SecurityGroup(self, "EcsToRdsSeurityGroup",
            vpc = vpc,
            description = "Allow WordPress containers to talk to RDS"
        )

        db_cred_generator = _lambda.Function(
            self, 'db_creds_generator',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='db_creds_generator.handler',
            code=_lambda.Code.asset('lambda'),
            environment={
                'test': 'test',
            }
        )

        #Set Permissions and Sec Groups
        rds_instance.connections.allow_from(EcsToRdsSeurityGroup, ec2.Port.tcp(3306))   #Open hole to RDS in RDS SG

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_efs/FileSystem.html
        FileSystem = efs.FileSystem(self, "MyEfsFileSystem",
            vpc=vpc,
            encrypted=True, # file system is not encrypted by default
            lifecycle_policy = efs_lifecycle_policy,
            performance_mode = efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode = efs.ThroughputMode.BURSTING,
            removal_policy = core.RemovalPolicy(efs_removal_policy),
            enable_automatic_backups = efs_automatic_backups
        )

        self.output_props = props.copy()
        self.output_props["vpc"] = vpc
        self.output_props["rds_instance"] = rds_instance
        self.output_props["EcsToRdsSeurityGroup"] = EcsToRdsSeurityGroup
        self.output_props["FileSystem"] = FileSystem
    
    @property
    def outputs(self):
        return self.output_props