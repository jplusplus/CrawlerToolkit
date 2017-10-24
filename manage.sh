#!/bin/bash

# Operations on django
django () {
  activate_venv
  ./crawler/manage.py $@
}

# Run crawler server locally
start_crawler () {
  activate_venv
  django runserver
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

# Run test site
start_test_site () {
  jekyll serve
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

if [[ "$(type -t $@)" =~ .*function ]];
then
    echo Starting "$@"
    eval $(printf "%q " "$@")
else
    echo "Function $@ not found, please check manage.sh file"
fi
