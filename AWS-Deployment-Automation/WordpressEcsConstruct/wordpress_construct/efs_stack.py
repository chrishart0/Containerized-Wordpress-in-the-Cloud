from aws_cdk import (
    core,
    aws_efs as efs
)

efs_removal_policy = "SNAPSHOT" #RETAIN
efs_lifecycle_policy = efs.LifecyclePolicy.AFTER_7_DAYS # https://docs.aws.amazon.com/efs/latest/ug/lifecycle-management-efs.html
efs_automatic_backups = True

class WordpressEfsConstructStack(core.Stack):

    def __init__(self, scope: core.Construct, construct_id: str, props, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs) 

        #https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_efs/FileSystem.html
        FileSystem = efs.FileSystem(self, "MyEfsFileSystem",
            vpc=props['vpc'],
            encrypted=True, # file system is not encrypted by default
            lifecycle_policy = efs_lifecycle_policy,
            performance_mode = efs.PerformanceMode.GENERAL_PURPOSE,
            throughput_mode = efs.ThroughputMode.BURSTING,
            removal_policy = core.RemovalPolicy(efs_removal_policy),
            enable_automatic_backups = efs_automatic_backups
        )

        self.output_props = props.copy()
        self.output_props["FileSystem"] = FileSystem

    @property
    def outputs(self):
        return self.output_props