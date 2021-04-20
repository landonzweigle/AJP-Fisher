#!/bin/sh

gradle build

./gradlew run > jLog &
sleep 2.5
python3 ./AutoFisher-Python/AutoFisher.py > pLog &



