import json
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
    aws_rds as rds,
    aws_efs as efs
)

class WordpressEcsConstructStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs) 

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_efs/FileSystem.html#aws_cdk.aws_efs.FileSystem.add_access_point
        #Access points allow multiple WordPress file systems to live on the same EFS Volume
        #The more data on an EFS volume the better it will preform
        #This provides a high level of security while also optimizing performance
        AccessPoint = props['file_system'].add_access_point( "local-access-point",
            path=f"/{props['IdentifierName']}",
            create_acl = efs.Acl(
                owner_uid="100", #https://aws.amazon.com/blogs/containers/developers-guide-to-using-amazon-efs-with-amazon-ecs-and-aws-fargate-part-2/
                owner_gid="101",
                permissions="0755"
            )
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/Cluster.html?highlight=ecs%20cluster#aws_cdk.aws_ecs.Cluster
        cluster = ecs.Cluster(self, "Cluster", 
            vpc = props['vpc'], 
            container_insights = props['ecs_enable_container_insights']
        )

        #Get needed secrets
        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ssm/StringParameter.html?highlight=from_secure_string_parameter_attributes#aws_cdk.aws_ssm.StringParameter.from_secure_string_parameter_attributes
        # ParameterStoreTest = ssm.StringParameter.from_secure_string_parameter_attributes( self, "ParameterStoreTest",
        #     parameter_name="", #Remeber, KMS permissions for task execution role for parameter store key!
        #     version=1
        # )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/Secret.html
        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_secretsmanager/SecretStringGenerator.html
        dbtest = {
            "database_name":'',
            "username":'',
            "host":str(props["rds_instance"].cluster_endpoint.hostname)
        }     
        WordpressDbConnectionSecret=secretsmanager.Secret(self, "WordpressDbConnectionSecret",
            generate_secret_string=secretsmanager.SecretStringGenerator(
                                secret_string_template=json.dumps(dbtest),
                                generate_string_key="password",
                                exclude_characters='/"'
                            )            
        )

        #ToDO: Lambda call to populate secrets but only 

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/Volume.html#aws_cdk.aws_ecs.Volume
        WordpressEfsVolume = ecs.Volume (
            name = "efs",
            efs_volume_configuration = ecs.EfsVolumeConfiguration(
                file_system_id = props['file_system'].file_system_id,
                transit_encryption = "ENABLED",
                authorization_config = ecs.AuthorizationConfig(
                    access_point_id = AccessPoint.access_point_id
                )
            )
        )

        #Create Task Definition
        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/FargateTaskDefinition.html
        WordpressTask = ecs.FargateTaskDefinition(self, "TaskDefinition",
            cpu = props['ecs_cpu_size'],
            memory_limit_mib = props['ecs_memory_size'],
            volumes=[WordpressEfsVolume]
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/FargateTaskDefinition.html#aws_cdk.aws_ecs.FargateTaskDefinition.add_container
        WordpressContainer = WordpressTask.add_container( "Wordpress",
            image=ecs.ContainerImage.from_ecr_repository(
                repository=ecr.Repository.from_repository_name(self, "wpimage",
                    repository_name = props['ecs_container_repo_name']
                ),
                tag=props['ecs_container_tag']
            ),
            logging=ecs.LogDriver.aws_logs(
                stream_prefix = "container",
                #log_group = "{props['environment']}/{props['unit']}/{props['application']}", #ToDo make sure I like log group name
                log_retention = logs.RetentionDays(props['ecs_log_retention_period'])
            ),
            environment = {"TROUBLESHOOTING_MODE_ENABLED": props['TROUBLESHOOTING_MODE_ENABLED']},
            secrets = {
                # "PARAMETERSTORETEST": ecs.Secret.from_ssm_parameter( ParameterStoreTest ),
                "DBHOST": ecs.Secret.from_secrets_manager( WordpressDbConnectionSecret, "host" ),
                "DBUSER": ecs.Secret.from_secrets_manager( WordpressDbConnectionSecret, "username" ),
                "DBUSERPASS": ecs.Secret.from_secrets_manager( WordpressDbConnectionSecret, "password" ),
                "DBNAME": ecs.Secret.from_secrets_manager( WordpressDbConnectionSecret, "database_name" )
            },
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/ContainerDefinition.html?highlight=add_port_mappings#aws_cdk.aws_ecs.ContainerDefinition.add_port_mappings
        WordpressContainer.add_port_mappings(
            ecs.PortMapping( container_port=80, protocol=ecs.Protocol.TCP)
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/ContainerDefinition.html?highlight=add_port_mappings#aws_cdk.aws_ecs.ContainerDefinition.add_port_mappings
        #https://gist.github.com/phillippbertram/ee312b09c3982d76b9799653ed6d6201
        WordpressContainer.add_mount_points(
            ecs.MountPoint(
                container_path = "/var/www/localhost/htdocs/wp-content/",
                read_only = False,
                source_volume = WordpressEfsVolume.name
            )
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs_patterns/ApplicationLoadBalancedFargateService.html
        EcsService = ecs_patterns.ApplicationLoadBalancedFargateService(self, "EcsService",
            cluster = cluster,
            desired_count = props['ecs_container_desired_count'],
            task_definition = WordpressTask,
            enable_ecs_managed_tags = True,
            public_load_balancer = True,
            domain_name=props['domain_name'],
            domain_zone= route53.HostedZone.from_hosted_zone_attributes(self, "hostedZone", hosted_zone_id=props['domain_zone'], zone_name=props['zone_name']) ,
            listener_port=443,
            redirect_http=True,
            protocol=elasticloadbalancingv2.ApplicationProtocol("HTTPS"),
            target_protocol=elasticloadbalancingv2.ApplicationProtocol("HTTP"),
            platform_version = ecs.FargatePlatformVersion("VERSION1_4"), #Required for EFS
            security_groups = [
                ec2.SecurityGroup.from_security_group_id(self, "EcsToRdsSeurityGroup", security_group_id=props["EcsToRdsSeurityGroup"].security_group_id)
            ],
        )

        #https://gist.github.com/phillippbertram/ee312b09c3982d76b9799653ed6d6201
        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Connections.html#aws_cdk.aws_ec2.Connections
        EcsService.service.connections.allow_to(props['file_system'], ec2.Port.tcp(2049))   #Open hole to ECS in EFS SG

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_elasticloadbalancingv2/ApplicationTargetGroup.html#aws_cdk.aws_elasticloadbalancingv2.ApplicationTargetGroup.set_attribute
        EcsService.target_group.set_attribute(
            key="load_balancing.algorithm.type",
            value="least_outstanding_requests"
        )
        EcsService.target_group.set_attribute(
            key="deregistration_delay.timeout_seconds",
            value="30"
        )
        EcsService.target_group.configure_health_check(
            healthy_threshold_count=5, #2-10
            timeout=core.Duration.seconds(29),
        )

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ecs/FargateService.html#aws_cdk.aws_ecs.FargateService.auto_scale_task_count
        ECSAutoScaler = EcsService.service.auto_scale_task_count(max_capacity=props['ecs_container_max_count'], min_capacity=props['ecs_container_min_count'])

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