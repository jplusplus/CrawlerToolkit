# Offshore Journalism Toolkit
The crawler toolkit is part of the [Offshore Journalism](http://www.offshorejournalism.com) initiative. It's a proof-of-concept of the `preversation` meta tag. Thus this project is divided in two parts, first the crawler, a django application designed to crawl feeds (RSS, atom or Twitter account) and preserve, if needed, articles tagged with preservation meta. The second part (the test site) is dedicated to test the preservation tags. It implements a simple version of the preservation meta tags and is based on Jekyll. 

## Summary
- [How to install](#how-to-install)
  - [Prerequisites](#prerequisites)
  - [Get the sources](#get-the-sources)
  - [Install](#install)
- [Configuration](#configure-the-application)
  - [The environnement variables](#the-environnement-variables)
  - [Set up external services](#set-up-the-external-services)
- [How to use](#how-to-use)
  - [Run servers locally](#run-servers-locally)
  - [Operations on the django application](#operations-on-the-django-application)
  - [Operations on the jekyll application](#operations-on-the-jekyll-application)
  - [Adding content on the test site](#adding-content-on-the-test-site)
- [How to deploy](#how-to-deploy)
  - [Deploy the crawler](#deploy-the-crawler)
  - [Deploy the test site](#deploy-the-test-site)


## How to install
### Prerequisites
To install all dependencies (see [Dependencies]()) you must have the following programs installed on your computer:

- python (>= 3.5)
- ruby (>= 2.4)
- homebrew is recommanded if you're on Mac OS X
- rvm is also recommanded

### Get the sources
```sh
git clone https://github.com/jplusplus/CrawlerToolkit.git
cd CrawlerToolkit

```

### Install
#### 1. Install redis
```sh
# On Mac OS X (with homebrew)
brew install redis

# On Ubuntu (16.04+) 
sudo apt-get install redis-server

# On RedHat/Fedora distributions
sudo dnf install redis
```

#### 2. Install the dependencies
```sh
./manage.sh install
```

## Configure the application
### The environnement variables
This application relies on environnement variable to run. 

| Name | Purpose |
| ---- | ------- |
| `DJANGO_SETTINGS_MODULE` | Change the settings file to use for the django app (ex `settings_dev` and `settings_heroku`) |
| `AWS_ACCESS_KEY_ID` | Amazon Web Service acces key's id, required on heroku to serve & upload static files. |
| `AWS_SECRET_ACCESS_KEY` | As above, required for static files serving & uploading. |
| `AWS_STORAGE_BUCKET_NAME` | The name of the S3 storage bucket |
| `TWITTER_ACCESS_TOKEN` | Token to access [Twitter's API](#twitter) |
| `TWITTER_ACCESS_SECRET`| Acces's secret for [Twitter's API](#twitter) |
| `TWITTER_CONSUMER_KEY`| Twitter consumer key for [Twitter's API](#twitter) |
| `TWITTER_CONSUMER_SECRET`| Token to access [Twitter's API](#twitter) |

#### On local
To configure the local application we use and `.env` file. To configure it copy the `.env.template` file:
```sh
cp .env.template .env
```
Then edit `.env` to fill the proper variables

#### On Heroku
All configuration variables can be edited from the heroku dashboard or with the following command.
```sh
# To set a variable
./manage.sh set <VARIABLE NAME> <value>
# To get a variable's value
./manage.sh get <VARIABLE NAME>
```

### Set up the external services
This project has been configured to be managed with simple commands (see How to use). But in order certain services
needs to be configured.
#### Surge.sh
You will need to install the surge npm package to deploy the test-site.
```sh
$ sudo npm install -g surge
$ surge login
```

#### Heroku
To use the heroku `manage.sh` commands you must have the heroku-cli package installed on your OS. Once this package
is installed you must log in:
```sh
$ heroku login
```
Then add the proper `heroku` git remote with the following command
```sh
# replace <app> with your heroku's application name
$ heroku git:remote -a <app>
```

#### Twitter
This project uses the Twitter's API in order to retrieve tweets from twitter feeds. Thus, you'll need to [create a twitter app](https://apps.twitter.com/app/new) and generate a set of Token Access (in the Keys and Access Tokens tab). Then report the various keys, secrets and tokens in the appropriate [environnement variables](#the-environnement-variables)

## How to use
### Run servers locally

```sh
# 1. Start the redis server
./manage.sh start_redis <optional port, default: 3000>

# 2. Run the crawler
./manage.sh start_crawler <optional port, default: 4000>

# 3. Run the test site
./manage start_test_site <optional port, default 5000>
``` 

### Operations on the django application
If you need to perform operations on the application you have access to all django commands throught the following command:
```sh
./manage.sh django --help
```

### Operations on the jekyll application
```sh
./manage.sh jekyll --help
```

## How to deploy

### Deploy the crawler
The crawler itself is parametered to be deployed on heroku with the following command
```sh
# This helper function calls the following git command:
# git subtree push --prefix crawl/ heroku master
./manage.sh deploy
```
### Deploy the test site
By default we parametered the `test-site` to be deployed on [surge.sh](http://surge.sh).
```sh
$ ./manage.sh deploy_test_site
``` 

## Adding content on the test site
Currently, the test site is built thanks to Jekyll and the minimal-mistakes theme.
So in order to make a new post work properly you'll need to create a post in `tests-site/_posts`
folder (like on Jekyll) but with the `single` layout instead of the `post` that you'd expect.

Also, the purpose of this site is to test the preservation meta tags (see the specs).
To do add one or more preservation meta tag you just have to add a `preservation` field in the post header as follows:

```md
---
layout: single
title: "The article title"
categories: this is a test
preservation:
  - type: notfound_only
    value: true
  - type: release_date
    value: 2018-01-01
  - type: priority
    value: true
---
