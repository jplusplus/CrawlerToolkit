# Offshore Journalism Toolkit 


## How to install
### Prequisites
To install all dependencies (see [Dependencies]()) you must have the following programs installed on your computer:

- python (>= 3.4)
- ruby (>= 2.4)
- rvm is also recommanded

### Get the sources
```sh
# if you have the rights to edit this repo
git clone git@github.com:pbellon/CrawlerToolkit.git
# Otherwise
git clone https://github.com/pbellon/CrawlerToolkit.git

```

### Install
```sh
./manage.sh install
```

## How to use

### Run servers 
The application comes with 2 parts: 
- the crawler itself
- the site to test it against. 

Run the crawler
```sh

./manage.sh start_crawler
```

Run the test site
```sh
./manage start_test_site
``` 

### Operation on the django application
If you need to perform operations on the application you have access to all django commands throught the following command:
```sh
./manage.sh django --help
```

### Operation on the jekyll application
```sh
./manage.sh jekyll --help
```

## Deploy

### Deploy the crawler
The crawler itself is parametered to be deployed on heroku.


### Deploy the test server to github pages
