#!/usr/bin/env python3

from aws_cdk import core

from wordpress_construct.base_stack import WordpressBaseConstructStack
from wordpress_construct.ecs_stack import WordpressEcsConstructStack

env = core.Environment(region="us-east-1")

props = {
            'namespace':'wordpress',
            'farm':'',
        }

app = core.App()
base_stack = WordpressBaseConstructStack(app, f"{props['namespace']}{props['farm']}-base-construct", props=props, env=env)

ecs_stack = WordpressEcsConstructStack(app, f"{props['namespace']}{props['farm']}-ecs-construct", base_stack.outputs , env=env)
ecs_stack.add_dependency(base_stack)

app.synth()
