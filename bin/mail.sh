#!/bin/sh

# mail -a "Content-type: text/html;" -s HTMLtest dc108349@gmail.com < email_html.html
mail -a "Content-type: text/html;" -s "$1" $2 < email.html
