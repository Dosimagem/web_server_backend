export $(/opt/elasticbeanstalk/bin/get-config --output YAML environment | sed 's/: /=/' | xargs)