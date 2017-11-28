#!/bin/bash

VENV_BIN=.venv/bin
TEST_SITE_DOMAIN='offshorecrawler-rss-feed.surge.sh'
TEST_SITE_BUILD_FOLDER='test-site-build'

# Operations on django
admin () {
  setup_env
  django-admin $@
}

_heroku() {
  remote=$1
  args=("$@")
  args=${args[@]:1}
  heroku $args --remote $remote
}

# Usage: _django_heroku <git remote branch> 
_django_heroku () {
  remote=$1
  args=("$@")
  args=${args[@]:1}
  heroku run python manage.py $args --remote $remote
}

django_heroku () {
  _django_heroku heroku $@
}

django () {
  setup_env
  ./crawler/manage.py $@
}

shell() {
  django shell
}

makemigrations () {
  django makemigrations
}

migrate () {
  django migrate
}

python_shell() {
  setup_env
  cd crawler
  ipython
  cd -
}

# VIRTUALENV FUNCTIONS
install_venv () {
  pip3 install --user virtualenv
  virtualenv -p python3 .venv
}

setup_env () {
  if [ -f .env ]
  then
    echo ".env file found, sourcing it for environnement variables" 
    source .env
  fi;
  source .venv/bin/activate
}

install_python_deps () {
  echo Installing python dependencies
  pip install -r crawler/requirements.txt
}

update_requirements () {
  setup_env
  pip freeze > crawler/requirements.txt
}

pip () {
  ./$VENV_BIN/pip $@
}

remote_bundle () {
  cd test-site
  bundle $@
  cd ..
}

# Operations on jekyll 
jekyll () {
  remote_bundle exec jekyll $@
}


install_ruby_deps () {
  echo Installing ruby dependencies
  # If bundle command doesn't exist we install the bundler gem
  if ! type bundle > /dev/null; then
     gem install bundler
  fi
  remote_bundle install
}


install () {
  install_venv
  setup_env
  install_python_deps
  install_ruby_deps
}

# Run crawler server locally
start_crawler () {
  port=${1:-4000}
  django runserver $port 
}

# Run test site
start_test_site () {
  port=${1:-5000}
  jekyll serve --port $port
}

start_redis () {
  port=${1:-3000}
  redis-server --port $port
}

start_celery () {
  setup_env
  cd crawler
  celery -A crawler worker -l info -B -E
  cd -
}

start () {
  tmux new-session -d -s config './manage.sh start_crawler'
  tmux split-window -v -t config './manage.sh start_redis'
  tmux split-window -h -t config './manage.sh start_test_site'
  tmux split-window -v -t config './manage.sh start_celery'
  tmux -2 attach-session -t config
}

set(){
    _h config:set $1=$2
}
get(){
    _h config:get $1
}

_h(){
    heroku $@ --remote heroku
}

# DEPLOY COMMANDS
# usage: deploy_heroku <remote-branche-name>
deploy_heroku () {
  git subtree push --prefix crawler/ $1 master  
}

build_test_site() {
  jekyll build -d ../$TEST_SITE_BUILD_FOLDER 
}

push_test_site() {
  git add $TEST_SITE_BUILD_FOLDER
  git commit -m "Update build" 
  git subtree push --prefix $TEST_SITE_BUILD_FOLDER pages gh-pages
}
deploy_test_site () {
  build_test_site
  push_test_site
}

deploy () {
  deploy_heroku heroku
}

# deploy to crawler-toolkit-staging remote.
deploy_staging () {
  deploy_heroku heroku-staging
}

if [[ "$(type -t $@)" =~ .*function ]];
then
    eval $(printf "%q " "$@")
else
    echo "Function $@ not found, please check manage.sh file"
fi
