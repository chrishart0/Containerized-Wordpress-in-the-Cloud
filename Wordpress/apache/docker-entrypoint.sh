#!/bin/bash

#Configure Wordpress
/bin/bash /usr/bin/containerDebianApacheWordpressDeploy.sh

/bin/bash
#Start apache
httpd-foreground