#!/usr/bin/env python3

from aws_cdk import core

from wordpress_construct.vpc_stack import WordpressVpcConstructStack
from wordpress_construct.rds_stack import WordpressRdsConstructStack
from wordpress_construct.ecs_stack import WordpressEcsConstructStack

env = core.Environment(region="us-east-1")

props = {
            'namespace':'wordpress',
            'farm':'-kg',
            'vpc_name':'kg-vpc',
            'db_master_username': 'wordpress_user',
            'db_instance_identifier':'wordpress-db-instance',
            'db_instance_engine':'MYSQL'
        }

app = core.App()
vpc_stack = WordpressVpcConstructStack(app, f"{props['namespace']}{props['farm']}-vpc-construct", props=props, env=env)

rds_stack = WordpressRdsConstructStack(app, f"{props['namespace']}{props['farm']}-rds-construct", vpc_stack.outputs , env=env)
rds_stack.add_dependency(vpc_stack)

ecs_stack = WordpressEcsConstructStack(app, f"{props['namespace']}{props['farm']}-ecs-construct", rds_stack.outputs , env=env)
ecs_stack.add_dependency(rds_stack)


app.synth()
