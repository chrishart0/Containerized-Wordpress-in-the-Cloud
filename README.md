# Containerized-Wordpress-in-the-Cloud
Automate the deployment and management of cheap, high availability, containerized wordpress in the cloud. 

## Containers
* Run Alpine Linux for it's exceedingly small footprint and lack of bloat
* Run nginx
* Mount networked file system for shared web server directory contianer wordpress files
* Sit behind loadbalancer directing traffic

## DB
* MariaDB managed DB instance
* Optional read replica, left off by default to save costs

## Infrastrucutre as Code
* All infra deployments are automated with IaC tools for your convienicne 
