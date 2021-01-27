from aws_cdk import (
    core,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_lambda as _lambda
)

import json


class WordpressRdsConstructStack(core.Stack):

    def getDBEngine(self,engine):
        if(engine == 'MYSQL'):
            return rds.DatabaseInstanceEngine.MYSQL
        

    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_rds/DatabaseCluster.html
        ##TODO:ADD Aurora Serverless Option
        rds_instance = rds.DatabaseCluster(self,'wordpress-db',
            engine=rds.DatabaseClusterEngine.aurora_mysql(
                version=rds.AuroraMysqlEngineVersion.VER_2_07_2
            ),
            instance_props=rds.InstanceProps(
                vpc=props['vpc']
            )
        )

        EcsToRdsSeurityGroup= ec2.SecurityGroup(self, "EcsToRdsSeurityGroup",
            vpc = props['vpc'],
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

        self.output_props = props.copy()
        self.output_props["rds_instance"] = rds_instance
        self.output_props["EcsToRdsSeurityGroup"] = EcsToRdsSeurityGroup
    
    @property
    def outputs(self):
        return self.output_props