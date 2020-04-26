#bin/bash
$oldUrl="https://arcadian.cloud"
$newUrl="http://arcadian.cloud"

UPDATE wp_options SET option_value = replace(option_value, 'http://www.oldurl', 'http://www.newurl') WHERE option_name = 'home' OR option_name = 'siteurl';
UPDATE wp_posts SET guid = replace(guid, 'http://www.oldurl','http://www.newurl');
UPDATE wp_posts SET post_content = replace(post_content, 'http://www.oldurl', 'http://www.newurl');
UPDATE wp_postmeta SET meta_value = replace(meta_value,'http://www.oldurl','http://www.newurl');



mysql -u root --password="" -e "
UPDATE wp_options
SET option_value = 'http://new-domain-name.com'
WHERE option_name = 'home';
"

UPDATE wp_options
SET option_value = 'http://new-domain-name.com'
WHERE option_name = 'siteurl';

UPDATE wp_posts
SET post_content = REPLACE(post_content,'http://old-domain-name.com','http://new-domain-name.com');

UPDATE wp_posts
SET guid = REPLACE(guid,'http://old-domain-name.com','http://new-domain-name.com');

mysql -u root --password=""
use wordpressDB;
UPDATE wp_options SET option_value = "http://arcadian.cloud" WHERE option_value = 'https://arcadian.cloud';
