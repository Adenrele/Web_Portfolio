#!/bin/bash
pip freeze > requirements.txt
flyctl deploy --app portfolio-web-app
echo "Requirements file generated and app deployed to fly.io.\nWOOOOOOOOOOOOOOO"