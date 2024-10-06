#!/bin/bash
pip freeze > requirements.txt
flyctl deploy --app portfolio-web-app