from aws_cdk import (
    core, 
    aws_ec2 as ec2
)

cpvCIDR = "10.2.0.0/16"

class WordpressVpcConstructStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Example automatically generated. See https://github.com/aws/jsii/issues/826
        vpc = ec2.Vpc(self, "vpc",
            cidr=cpvCIDR,
            max_azs=3,
            subnet_configuration=[
                {
                    'cidrMask': 28,
                    'name': 'public',
                    'subnetType': ec2.SubnetType.PUBLIC
                },
                {
                    'cidrMask': 28,
                    'name': 'private',
                    'subnetType': ec2.SubnetType.PRIVATE
                },
                {
                    'cidrMask': 28,
                    'name': 'db',
                    'subnetType': ec2.SubnetType.ISOLATED
                }
            ]
        )

        self.output_props = props.copy()
        self.output_props["vpc"] = vpc
    
    @property
    def outputs(self):
        return self.output_props