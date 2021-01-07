# Containerized-Wordpress-in-the-Cloud
Automate the deployment and management of cheap, high availability, containerized wordpress in the cloud. 

![Build-Container-Alpine-Apache](https://github.com/ChristianHart/Containerized-Wordpress-in-the-Cloud/workflows/Build-Container-Alpine-Apache/badge.svg)

![awsInfraDiagram](AWS Deployment Automation/awsInfra.png)

## Containers
* Run Alpine Linux for it's exceedingly small footprint and lack of bloat
* Mount networked file system(EFS) for sharing wp-content allowing for ease of use and quick load times
* Sit behind ELB directing traffic and allowing for auto scaling
* HTTPS offload at loadbalancer for lower resource consumption
* CloudFront caching of uploaded files for quicker load times and less resource consumption

## Infrastrucutre as Code
* All infra deployments are automated with IaC tools for your convenience 
