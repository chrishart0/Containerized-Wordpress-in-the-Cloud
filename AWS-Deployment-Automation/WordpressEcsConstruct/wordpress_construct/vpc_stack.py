from aws_cdk import (
    core, 
    aws_ec2 as ec2,
)

cpvCIDR = "10.1.0.0/16"

class WordpressVpcConstructStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Vpc.html
        vpc = ec2.Vpc(self, "VPC", 
            max_azs=3,
            cidr=cpvCIDR
        )

        self.output_props = props.copy()
        self.output_props["vpc"] = vpc
    
    @property
    def outputs(self):
        return self.output_props