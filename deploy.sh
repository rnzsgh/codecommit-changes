#!/bin/bash

python -m py_compile lambda_function.py

zip -r handler.zip lambda_function.py ; aws lambda update-function-code --function-name CodeCommitChanges --publish --zip-file fileb://handler.zip



