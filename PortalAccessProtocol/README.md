This was an attempt to create a dedicated portal to "semi-automatically" add IPs to security groups. 

This was tested with an R-shiny app hosted on an EC2 instance.

It uses a Google Form as a way for authorized users to request new IPs get added to the EC2 instance hosting the app.

An authorized user checks incoming requests and runs a simple command to add the new IP.


## Server Side Changes
 1. Instal ModRewrite apache module - `sudo a2enmod rewrite`
 2. Disable / Comment out these lines in /etc/apache2/sites-enabled/000-default.conf to disable the reverse proxy. `#ProxyPass / http://0.0.0.0:3838/ & #ProxyPassReverse / http://0.0.0.0:3838/`
 3. Create a .htaccess file in /var/www folder which contains 
     - Options +FollowSymLinks
     - RewriteEngine On
     - RewriteRule ^.*$ auth.php

## AUTH.PHP script 
Whenever a user accesses the R-Shiny server - it will redirect them to an auth.php script that checks whether their IP is present in a {IP-Whitelist} file.

    If IP exists in the {Whitelist} {
      Auth.php redirects to requested URL 
    else
      it redirects them to [CaDC Analytics Portal access request form](https://goo.gl/forms/vpB3JTPSk3oDf4F92)

## GOOGLE APPS NOTIFICATION SCRIPT
I also wrote a custom Google Apps Script on the Response Spreadsheet of the [Portal Access Request Form](https://goo.gl/forms/vpB3JTPSk3oDf4F92). For any new row, it will send email to argo@argolabs.org notifying them of new access request.
https://script.google.com/a/macros/argolabs.org/s/AKfycbzKH_V3Ix6aNUazQzeZiJxBPO672cogWbEKZ8yCecxpUNvLEQ02/exec

## SYNCING w/AWS security groups
The {IP-Whitelist} file is updated on schedule by issuing:

    sudo aws ec2 describe-security-groups --group-ids sg-46b9723e | grep CidrIp | awk -F\" '{print $4}' | awk -F/ '{print $1}' >>whitelist

