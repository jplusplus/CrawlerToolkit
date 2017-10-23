#!/bin/bash

activate_venv() {
  source ./crawler/.venv/bin/activate
}

# Run crawler server locally
start_crawler () {
  activate_venv
  ./crawler/manage.py runserver
}

remote_bundle () {
  cd test-site
  bundle $@
  cd ..
}

# Run test site
start_test_site () {
  remote_bundle exec jekyll serve
}

install () {
  parameter_virtualenv
  parameter_bundle

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
