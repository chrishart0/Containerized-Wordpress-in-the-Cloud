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
        }

props['IdentifierName'] = f"{props['environment']}-{props['application']}-{props['unit']}"

app = core.App()
base_stack = WordpressBaseConstructStack(app, f"{props['IdentifierName']}-base-construct", props=props, env=env)

ecs_stack = WordpressEcsConstructStack(app, f"{props['IdentifierName']}-ecs-construct", base_stack.outputs , env=env)
ecs_stack.add_dependency(base_stack)

tagResources([base_stack,ecs_stack],props)

app.synth()
