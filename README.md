# Offshore Journalism Toolkit 


## How to install
### Prequisites
To install all dependencies (see [Dependencies]()) you must have the following programs installed on your computer:

- python (>= 3.4)
- ruby (>= 2.4)
- homebrew is recommanded if you're on Mac OS X
- rvm is also recommanded

### Get the sources
```sh
# if you have the rights to edit this repo
git clone git@github.com:pbellon/CrawlerToolkit.git
# Otherwise
git clone https://github.com/pbellon/CrawlerToolkit.git

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

#### *(optionnal) Install tmux*
We've created a way to locally run all services / parts of the application at once (See "Run all services in one command") however it depends on tmux in order to be able to create pane.
```sh
# On Mac OS X
brew install tmux
# On Debian-based distros
sudo apt-get install tmux
# On RedHat-based distros
sudo dnf install tmux 
``` 

## How to use

### Run servers 
The application comes with 2 parts: 
- the crawler itself
- the site to test it against. 

However it relies on redis in order to make Django & Celery work together (see Architecture). 

```sh
# 1. Run redis
./manage.sh start_redis

# 2. Run the crawler
./manage.sh start_crawler

# 3. Run the test site
./manage start_test_site
``` 

Or you can run all those services at once but it requires you to install tmux (see Install)
```sh
./manage start
```


### Operations on the django application
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
