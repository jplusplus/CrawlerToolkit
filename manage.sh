#!/bin/bash

# Operations on django
django () {
  activate_venv
  ./crawler/manage.py $@
}

makemigrations () {
  django makemigrations
}

migrate () {
  django migrate
}


install_python_deps () {
  echo Installing python dependencies
  pip install -r crawler/requirements.txt
}

update_requirements () {
  activate_venv
  pip freeze > crawler/requirements.txt
}

pip () {
  activate_venv
  pip3 $@
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
  remote_bundle install
}

# VIRTUALENV FUNCTIONS

install_venv () {
  pip3 install --user virtualenv
}

setup_venv () {
  virtualenv -p python3 .venv
}

activate_venv () {
  source .venv/bin/activate
}

install () {
  install_venv
  setup_venv
  activate_venv
  install_python_deps
  install_ruby_deps
}

# Run crawler server locally
start_crawler () {
  activate_venv
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

if [[ "$(type -t $@)" =~ .*function ]];
then
    echo Starting "$@"
    eval $(printf "%q " "$@")
else
    echo "Function $@ not found, please check manage.sh file"
fi
