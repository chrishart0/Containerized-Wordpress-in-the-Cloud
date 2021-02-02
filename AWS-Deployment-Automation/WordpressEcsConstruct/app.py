#!/usr/bin/env python3
from tagging_helper import tagResources
from aws_cdk import (
    core, 
    aws_efs as efs
)

from wordpress_construct.base_stack import WordpressBaseConstructStack
from wordpress_construct.ecs_stack import WordpressEcsConstructStack

env = core.Environment(region="us-east-1")

props = {
            'ecs_log_retention_period': 'THREE_MONTHS',
            'ecs_enable_container_insights': True,
            'ecs_cpu_size': 256,
            'ecs_memory_size': 512,
            'ecs_container_desired_count': 1,
            'ecs_container_max_count': 2,
            'ecs_container_min_count': 1,
            'ecs_container_efs_paths': {
                'RootWebDirectory': '/var/www/localhost/htdocs',
                'SubDirectoriesForEFS': ['/wp-content']
            },
            'efs_removal_policy':"SNAPSHOT", #RETAIN,
            'efs_lifecycle_policy': efs.LifecyclePolicy.AFTER_7_DAYS, # https://docs.aws.amazon.com/efs/latest/ug/lifecycle-management-efs.html
            'efs_automatic_backups': True,
            'rds_enable_performance_insights': False,
            'rds_instance_type': 't3.small',
            'rds_storage_encrypted': True,
            'rds_automated_backup_retention_days': 7,
            'deploy_bastion_host': True,
            ##############################
            ##############################
        }

props['IdentifierName'] = f"{props['environment']}-{props['application']}-{props['unit']}"

app = core.App()
base_stack = WordpressBaseConstructStack(app, f"{props['IdentifierName']}-base-construct", props=props, env=env)

ecs_stack = WordpressEcsConstructStack(app, f"{props['IdentifierName']}-ecs-construct", base_stack.outputs , env=env)
ecs_stack.add_dependency(base_stack)

tagResources([base_stack,ecs_stack],props)

app.synth()
