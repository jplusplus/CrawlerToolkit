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

install_python_deps () {
  echo Installing python dependencies
  pip3 install -r crawler/requirements.txt
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
  django runserver
}

# Run test site
start_test_site () {
  jekyll serve
}

start_redis () {
  redis-server --port 7878
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
