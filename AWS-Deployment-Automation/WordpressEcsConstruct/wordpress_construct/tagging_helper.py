from aws_cdk import core

def tagResources(resources, props):
    """
    Takes a list of resources and applies standard tags to them
    Takes props varibale for assigning tag values
    """
    for resource in resources:
        #https://docs.aws.amazon.com/cdk/latest/guide/tagging.html
        core.Tags.of(resource).add("Environment", props['environment'])
        core.Tags.of(resource).add("Application", props['application'])
        core.Tags.of(resource).add("Unit", props['unit'])