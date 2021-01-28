#!/usr/bin/env python3
from tagging_helper import tagResources
from aws_cdk import core

from wordpress_construct.base_stack import WordpressBaseConstructStack
from wordpress_construct.ecs_stack import WordpressEcsConstructStack

env = core.Environment(region="us-east-1")

props = {
            'application':'wordpress',
            'environment': 'Dev',
            'unit': 'chart',
        }

app = core.App()
base_stack = WordpressBaseConstructStack(app, f"{props['environment']}-{props['application']}-{props['unit']}-base-construct", props=props, env=env)

ecs_stack = WordpressEcsConstructStack(app, f"{props['environment']}-{props['application']}-{props['unit']}-ecs-construct", base_stack.outputs , env=env)
ecs_stack.add_dependency(base_stack)

tagResources([base_stack,ecs_stack],props)

app.synth()
