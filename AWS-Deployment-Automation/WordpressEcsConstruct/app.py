#!/usr/bin/env python3

from aws_cdk import core

from wordpress_construct.vpc_stack import WordpressVpcConstructStack
from wordpress_construct.efs_stack import WordpressEfsConstructStack
from wordpress_construct.ecs_stack import WordpressEcsConstructStack

env = core.Environment(region="us-east-1")

props = {
            'namespace':'wordpress',
            'farm':''
        }

app = core.App()
vpc_stack = WordpressVpcConstructStack(app, f"{props['namespace']}{props['farm']}-vpc-construct", props=props, env=env)

efs_stack = WordpressEfsConstructStack(app, f"{props['namespace']}{props['farm']}-efs-construct", vpc_stack.outputs , env=env)
efs_stack.add_dependency(vpc_stack)

ecs_stack = WordpressEcsConstructStack(app, f"{props['namespace']}{props['farm']}-ecs-construct", efs_stack.outputs , env=env)
ecs_stack.add_dependency(efs_stack)

app.synth()
