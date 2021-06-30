#!/bin/bash
EXIT=0

isort --settings-file setup.cfg --profile black flaskskeleton tests --diff || EXIT=1

black --check --line-length 120 flaskskeleton tests || EXIT=1

flake8 || EXIT=1

mypy flaskskeleton tests || EXIT=1

if [ $EXIT -eq 1 ]
then
    echo "FAIL"
else
    echo "GOOD"
fi

exit $EXIT
