from aws_cdk import (
    core, 
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_ecs_patterns as ecs_patterns,
    aws_ecr as ecr,
    aws_logs as logs,
    aws_ssm as ssm,
    aws_secretsmanager as secretsmanager,
    aws_iam as iam,
    aws_route53 as route53,
    aws_elasticloadbalancingv2 as elasticloadbalancingv2,
    aws_rds as rds
)

Environment = "Dev"
ProductName = "Wordpress"
SubProductName = "Test"
DBCredSecretsKey = "dev/db/wordpress/admin"
ContainerLogRetentionPeriod = "THREE_MONTHS"
ContainerRepoName = "alpine-apache-wordpress"
ContainerTag = "feature-cdk-init"
TROUBLESHOOTING_MODE_ENABLED = "false" #WARNING! SET THIS TO FALSE
cpvCIDR = "10.1.0.0/16"
domain_name="kg.wp.tedevops.com"
zone_name="wp.tedevops.com"
domain_zone="Z102380729N6XS64RENT3"
enable_container_insights=True
cpuSize = 256
memorySize = 512
containerDesiredCount = 1
containerMaxCount = 2
containerMinCount = 1

class WordpressEcsConstructStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/Cluster.html?highlight=ecs%20cluster#aws_cdk.aws_ecs.Cluster
        cluster = ecs.Cluster(self, "Cluster", 
            vpc=props['vpc'], 
            container_insights=enable_container_insights
        )

        #Get needed secrets
        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ssm/StringParameter.html?highlight=from_secure_string_parameter_attributes#aws_cdk.aws_ssm.StringParameter.from_secure_string_parameter_attributes
        # ParameterStoreTest = ssm.StringParameter.from_secure_string_parameter_attributes( self, "ParameterStoreTest",
        #     parameter_name="", #Remeber, KMS permissions for task execution role for parameter store key!
        #     version=1
        # )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_secretsmanager/Secret.html#aws_cdk.aws_secretsmanager.Secret.from_secret_name_v2
        SecretsManagerTest = secretsmanager.Secret.from_secret_name_v2( self, "SecretsManagerTest",
            secret_name=DBCredSecretsKey
        )

        #Create Task Definition
        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/FargateTaskDefinition.html
        WordpressTask = ecs.FargateTaskDefinition(self, "TaskDefinition",
            cpu = cpuSize,
            memory_limit_mib = memorySize,
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/FargateTaskDefinition.html#aws_cdk.aws_ecs.FargateTaskDefinition.add_container
        WordpressContainer = WordpressTask.add_container( "Wordpress",
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr.Repository.from_repository_name(self, "wpimage",
                    repository_name = ContainerRepoName
                ),
                tag=ContainerTag
            ),
            logging=ecs.LogDriver.aws_logs(
                stream_prefix="container",
                #log_group="{Environment}/{ProductName}/{SubProductName}", #ToDo make sure I like log group name
                log_retention=logs.RetentionDays(ContainerLogRetentionPeriod)
            ),
            environment={"TEST": "1", "TEST2": "2", "TROUBLESHOOTING_MODE_ENABLED": TROUBLESHOOTING_MODE_ENABLED},
            secrets = {
                # "PARAMETERSTORETEST": ecs.Secret.from_ssm_parameter( ParameterStoreTest ),
                "DBHOST": ecs.Secret.from_secrets_manager( SecretsManagerTest, "host" ),
                "DBUSER": ecs.Secret.from_secrets_manager( SecretsManagerTest, "username" ),
                "DBUSERPASS": ecs.Secret.from_secrets_manager( SecretsManagerTest, "password" ),
                "DBNAME": ecs.Secret.from_secrets_manager( SecretsManagerTest, "database_name" )
            },
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/ContainerDefinition.html?highlight=add_port_mappings#aws_cdk.aws_ecs.ContainerDefinition.add_port_mappings
        WordpressContainer.add_port_mappings(
            ecs.PortMapping( container_port=80, protocol=ecs.Protocol.TCP)
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedFargateService.html
        EcsService = ecs_patterns.ApplicationLoadBalancedFargateService(self, "EcsService",
            cluster = cluster,
            desired_count = containerDesiredCount,
            task_definition = WordpressTask,
            enable_ecs_managed_tags = True,
            public_load_balancer = True,
            domain_name=domain_name,
            domain_zone= route53.HostedZone.from_hosted_zone_attributes(self, "hostedZone", hosted_zone_id=domain_zone, zone_name=zone_name) ,
            listener_port=443,
            redirect_http=True,
            protocol=elasticloadbalancingv2.ApplicationProtocol("HTTPS"),
            target_protocol=elasticloadbalancingv2.ApplicationProtocol("HTTP"),
            platform_version = ecs.FargatePlatformVersion("VERSION1_4"), #Required for EFS
            security_groups = [
                ec2.SecurityGroup.from_security_group_id(self, "EcsToRdsSeurityGroup", security_group_id=props["EcsToRdsSeurityGroup"].security_group_id)
            ],
        )
          

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/FargateService.html#aws_cdk.aws_ecs.FargateService.auto_scale_task_count
        ECSAutoScaler = EcsService.service.auto_scale_task_count(max_capacity=containerMaxCount, min_capacity=containerMinCount)

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/ScalableTaskCount.html#aws_cdk.aws_ecs.ScalableTaskCount
        ECSAutoScaler.scale_on_cpu_utilization( "cpuScale", 
            target_utilization_percent = 80,
            scale_out_cooldown = core.Duration.seconds(30),
            scale_in_cooldown = core.Duration.seconds(60)
        )
        ECSAutoScaler.scale_on_memory_utilization( "memScale", 
            target_utilization_percent = 80,
            scale_out_cooldown = core.Duration.seconds(30),
            scale_in_cooldown = core.Duration.seconds(60)
        )
        #https://gist.github.com/phillippbertram/ee312b09c3982d76b9799653ed6d6201
        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Connections.html#aws_cdk.aws_ec2.Connections
        #EcsService.service.connections.allow_to(props['rds_instance'], ec2.Port.tcp(3306))   #Open hole to RDS in RDS SG
        
        #EcsService.service.connections.add_security_group(ec2.SecurityGroup.from_security_group_id(self, "EcsToRdsSeurityGroup", security_group_id=props["EcsToRdsSeurityGroup"].security_group_id) )