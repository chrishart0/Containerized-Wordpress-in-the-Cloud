#!/usr/bin/env python3

from aws_cdk import core

from wordpress_ecs_construct.wordpress_ecs_construct_stack import WordpressEcsConstructStack


app = core.App()
WordpressEcsConstructStack(app, "wordpress-ecs-construct", env={'region': 'us-east-1'})

app.synth()
