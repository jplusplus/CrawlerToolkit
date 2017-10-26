#!/bin/bash

VENV_BIN=.venv/bin

# Operations on django
admin () {
  setup_env
  django-admin $@
}

django () {
  setup_env
  ./crawler/manage.py $@
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

install_python_deps () {
  echo Installing python dependencies
  _pip install -r crawler/requirements.txt
}

update_requirements () {
  setup_env
  _pip freeze > crawler/requirements.txt
}

_pip () {
  setup_env
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

# VIRTUALENV FUNCTIONS

install_venv () {
  pip install --user virtualenv
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

install () {
  install_venv
  setup_env
  install_python_deps
  install_ruby_deps
}

# Run crawler server locally
start_crawler () {
  setup_env
  migrate
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

start () {
  tmux new-session -d -s config './manage.sh start_crawler'
  tmux split-window -h -t config './manage.sh start_redis'
  tmux split-window -v -t config './manage.sh start_test_site'
  tmux -2 attach-session -t config
}

# DEPLOY COMMANDS
# usage: deploy_heroku <remote-branche-name>
deploy_heroku () {
  git subtree push --prefix crawler $1 master  
}

# deploy to crawler-toolkit-staging remote.
deploy_staging () {
  deploy_heroku heroku-staging
}

if [[ "$(type -t $@)" =~ .*function ]];
then
    echo Starting "$@"
    eval $(printf "%q " "$@")
else
    echo "Function $@ not found, please check manage.sh file"
fi
