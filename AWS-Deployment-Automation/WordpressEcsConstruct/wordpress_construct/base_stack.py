import json
from aws_cdk import (
    core,
    aws_rds as rds,
    aws_ec2 as ec2,
    aws_lambda as _lambda,
    aws_efs as efs,
    aws_secretsmanager as secretsmanager,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_iam as iam
)

class WordpressBaseConstructStack(core.Stack):

    def getDBEngine(self,engine):
        if(engine == 'MYSQL'):
            return rds.DatabaseInstanceEngine.MYSQL
        
    def __init__(self, scope: core.Construct, id: str, props, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Vpc.html
        vpc = ec2.Vpc(self, "vpc",
            cidr=props['vpc_CIDR'],
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

        rds_subnetGroup = rds.SubnetGroup(self, "rds_subnetGroup",
            description = f"Group for {props['environment']}-{props['application']}-{props['unit']} DB",
            vpc = vpc,
            vpc_subnets = ec2.SubnetSelection(subnet_type= ec2.SubnetType.ISOLATED)
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_rds/DatabaseCluster.html
        ##TODO:ADD Aurora Serverless Option
        rds_instance = rds.DatabaseCluster(self,'wordpress-db',
            engine=rds.DatabaseClusterEngine.aurora_mysql(
                version=rds.AuroraMysqlEngineVersion.VER_2_07_2
            ),
            instances=1,
            instance_props=rds.InstanceProps(
                vpc=vpc,
                enable_performance_insights=props['rds_enable_performance_insights'],
                instance_type=ec2.InstanceType(instance_type_identifier=props['rds_instance_type'])
            ),
            subnet_group=rds_subnetGroup,
            storage_encrypted=props['rds_storage_encrypted'],
            backup=rds.BackupProps(
                retention=core.Duration.days(props['rds_automated_backup_retention_days'])
            )
        )

        EcsToRdsSeurityGroup= ec2.SecurityGroup(self, "EcsToRdsSeurityGroup",
            vpc = vpc,
            description = "Allow WordPress containers to talk to RDS"
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_lambda/Function.html
        db_cred_generator = _lambda.Function(
            self, 'db_creds_generator',
            runtime=_lambda.Runtime.PYTHON_3_8,
            handler='db_creds_generator.handler',
            code=_lambda.Code.asset('lambda/db_creds_generator'),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type= ec2.SubnetType.ISOLATED),        #vpc.select_subnets(subnet_type = ec2.SubnetType("ISOLATED")).subnets ,
            environment={
                'SECRET_NAME': rds_instance.secret.secret_name,
            }
        )

        #Set Permissions and Sec Groups
        rds_instance.connections.allow_from(EcsToRdsSeurityGroup, ec2.Port.tcp(3306))   #Open hole to RDS in RDS SG

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_efs/FileSystem.html
        file_system = efs.FileSystem(self, "MyEfsFileSystem",
            vpc = vpc,
            encrypted=True, # file system is not encrypted by default
            lifecycle_policy = props['efs_lifecycle_policy'],
            performance_mode = efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode = efs.ThroughputMode.BURSTING,
            removal_policy = core.RemovalPolicy(props['efs_removal_policy']),
            enable_automatic_backups = props['efs_automatic_backups']
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/Cluster.html?highlight=ecs%20cluster#aws_cdk.aws_ecs.Cluster
        cluster = ecs.Cluster(self, "Cluster", 
            vpc = vpc, 
            container_insights = props['ecs_enable_container_insights']
        )

        if props['deploy_bastion_host']:
            #ToDo: Deploy bastion host with a key file
            #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/BastionHostLinux.html
            bastion_host = ec2.BastionHostLinux(self, 'bastion_host',
                vpc = vpc
            )
            rds_instance.connections.allow_from(bastion_host, ec2.Port.tcp(3306))

            #######################
            ### Developer Tools ###
            # SFTP into the EFS Shared File System

            NetToolsSecret=secretsmanager.Secret(self, "NetToolsSecret",
                generate_secret_string=secretsmanager.SecretStringGenerator(
                    secret_string_template=json.dumps({
                        "username":'sftp',
                        "ip":''
                    }  ),
                    generate_string_key="password",
                    exclude_characters='/"'
                )            
            )

            #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_efs/FileSystem.html#aws_cdk.aws_efs.FileSystem.add_access_point
            AccessPoint = file_system.add_access_point( "access-point",
                path="/",
                create_acl = efs.Acl(
                    owner_uid="100", #https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-2/
                    owner_gid="101",
                    permissions="0755"
                )
            )

            EfsVolume = ecs.Volume (
                name = "efs",
                    efs_volume_configuration = ecs.EfsVolumeConfiguration(
                        file_system_id = file_system.file_system_id,
                        transit_encryption = "ENABLED",
                        authorization_config = ecs.AuthorizationConfig(
                            access_point_id = AccessPoint.access_point_id
                        )
                    )
                )
            

            #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/FargateTaskDefinition.html
            NetToolsTask = ecs.FargateTaskDefinition(self, "TaskDefinition",
                cpu = 256,
                memory_limit_mib = 512,
                volumes = [EfsVolume]
            )

            #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/FargateTaskDefinition.html#aws_cdk.aws_ecs.FargateTaskDefinition.add_container
            NetToolsContainer = NetToolsTask.add_container("NetTools", 
                image=ecs.ContainerImage.from_registry('netresearch/sftp'),
                command=['test:test:::efs']
            )
            NetToolsContainer.add_port_mappings( ecs.PortMapping( container_port=22, protocol=ecs.Protocol.TCP) )
            
            NetToolsContainer.add_mount_points(
                ecs.MountPoint(
                    container_path = "/home/test/efs", #ToDo build path out with username from secret
                    read_only = False,
                    source_volume = EfsVolume.name,
                )
            )

            #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/FargateService.html?highlight=fargateservice#aws_cdk.aws_ecs.FargateService
            service = ecs.FargateService(self, "Service",
                cluster=cluster,
                task_definition=NetToolsTask,
                platform_version = ecs.FargatePlatformVersion("VERSION1_4"), #Required for EFS
            )
            #ToDo somehow store container's IP on deploy

            #Allow traffic to EFS Volume from Net Tools container
            service.connections.allow_to(file_system, ec2.Port.tcp(2049)) 
            #ToDo allow bastion host into container on port 22

            #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_lambda/Function.html
            bastion_ip_locator = _lambda.Function( self, 'bastion_ip_locator',
                function_name=f"{props['environment']}-{props['application']}-{props['unit']}-SFTP-IP",
                runtime=_lambda.Runtime.PYTHON_3_8,
                handler='bastion_ip_locator.handler',
                code=_lambda.Code.asset('lambda/bastion_ip_locator'),
                environment={
                    'CLUSTER_NAME': cluster.cluster_arn,
                    'SERVICE_NAME': service.service_name
                }
            )

            #Give needed perms to bastion_ip_locator for reading info from ECS
            bastion_ip_locator.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "ecs:DescribeTasks"
                    ],
                    resources=[
                        #f"arn:aws:ecs:us-east-1:348757191778:service/{cluster.cluster_name}/{service.service_name}",
                        f"arn:aws:ecs:us-east-1:348757191778:task/{cluster.cluster_name}/*"
                    ]
                )
            )
            bastion_ip_locator.add_to_role_policy(
                iam.PolicyStatement(
                    actions=[
                        "ecs:ListTasks",
                    ],
                    resources=[ "*" ],
                    conditions={ 
                        'ArnEquals': { 'ecs:cluster': cluster.cluster_arn } 
                    }
                )
            )

        self.output_props = props.copy()
        self.output_props["vpc"] = vpc
        self.output_props["rds_instance"] = rds_instance
        self.output_props["EcsToRdsSeurityGroup"] = EcsToRdsSeurityGroup
        self.output_props["file_system"] = file_system
        self.output_props["cluster"] = cluster
    
    @property
    def outputs(self):
        return self.output_props