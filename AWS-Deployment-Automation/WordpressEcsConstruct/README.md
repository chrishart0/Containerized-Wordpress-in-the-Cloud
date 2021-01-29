
# Welcome to the Containerized Wordpress CDK Python project!

This project is written in Python with AWS CDK.

The `cdk.json` file tells the CDK Toolkit how to execute the app.

## Manual Deploy Process

Firstly, ensure python3 is installed

```
$ python3 --version
```

Next, follow these instructions to install the AWS CDK if you have no already done so:
https://docs.aws.amazon.com/cdk/latest/guide/getting_started.html

Ensure your working directory is .../AWS-Deployment-Automation/WordpressEcsConstruct

Next, manually create a virtualenv on MacOS and Linux:

```
$ python3 -m venv .venv
```

After the init process completes and the virtualenv is created, you can use the following
step to activate your virtualenv.

```
$ source .venv/bin/activate
```

If you are a Windows platform, you would activate the virtualenv like this:

```
% .venv\Scripts\activate.bat
```

Once the virtualenv is activated, you can install the required dependencies.

```
$ pip install -r requirements.txt
```

At this point you can now synthesize the CloudFormation template for this code.

```
$ cdk synth
```

To add additional dependencies, for example other CDK libraries, just add
them to your `setup.py` file and rerun the `pip install -r requirements.txt`
command.

## Useful commands

 * `cdk ls`          list all stacks in the app
 * `cdk synth`       emits the synthesized CloudFormation template
 * `cdk deploy`      deploy this stack to your default AWS account/region
 * `cdk diff`        compare deployed stack with current state
 * `cdk docs`        open CDK documentation

Enjoy!

## Options

### Troubleshooting mode
Set the `TROUBLESHOOTING_MODE_ENABLED` variable to true in [wordpress_ecs_construct_stack.py](AWS-Deployment-Automation/WordpressEcsConstruct/wordpress_ecs_construct/wordpress_ecs_construct_stack.py)

This does several things:
* In wp_config, sets the flag for WP_DEBUG to true
* Creates a health.html file in the root web dir
* Creates a health.php file in the root web dir

WARNING! Don't leave this option on in production. It will divulge info about your deployment that you do not want publicly available.

### Bastion Host
The base stack has the option to deploy a bastion host if the `deploy_bastion_host` flag is set to `True`

You should only leave the bastion host up for the time you are using it. After you are done set the flag back to `False` and get rid of it.

To connect to the bastion host using the following process
```
#Prereq: Install the aws session manager plugin if you have not already: https://docs.aws.amazon.com/systems-manager/latest/userguide/session-manager-working-with-install-plugin.html

#First, locate the bastion host instance ID

#Run the below command, make sure to change out instance-id with the correct instance ID
aws ssm start-session --target instance-id
```