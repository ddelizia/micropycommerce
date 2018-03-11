[![CircleCI](https://circleci.com/gh/ddelizia/micropycommerce.svg?style=svg)](https://circleci.com/gh/ddelizia/micropycommerce)

An attempt to connect together multiple systems

#Documentation

##Connected systesms

* Prestashop
* Ebay
* Firebase
* Google Spreadsheets
* Amazon
* Google Merchant

## Webservices

The system exposes a graphql endpoints to the url: `/graphql`

## Configuration

Configuration happens via config file. By default the configuration is taken from path `./config/env.yml` but this path can be set via the environment variable `CONFIG_FILE`

Example configuration:

```
firebase:
  databaseURL: https://<bd>.firebaseio.com
prestashop:
  url: https://<url>/api
  apiKey: <api key>
  mainLanguage: <lanuage>
environmet:
  templateFolder: "./handlebars/"
  fileFolder: <path for images>
  printConfig: false
  printXml: false
  log:
    level: "DEBUG"
    file:
      active: false
      filePath: /Path to log file
ws:
  username: <username>
  password: <password>
  port: <port>
ebay:
  # https://developer.ebay.com/DevZone/account/
  domain: api.sandbox.ebay.com
  # production api.ebay.com
  debug: true
  devid: <devid>
  appid: <appid>
  certid: <certid>
  token: <token>
  data:
    item:
        paypalEmail: <paypal-email>
        address:
            firstName: <Ebay first name>
            lastName: <Ebay last name>
google:
  categoryFeed: https://www.google.com/basepages/producttype/taxonomy-with-ids.it-IT.txt
```

### Configuration encryption

You have the possibility to encrypt the configuration file in order to hide the general configuration

Password must be set on the system in the variable: `DECRYPTION_PASS`

In order to encrypt a yaml file execute the following command line tool:
```
python tools.py --encrypt --file config/<env.yml> --key <password>
```