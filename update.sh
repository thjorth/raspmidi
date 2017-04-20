#!/bin/bash

ps -ef | grep "python .*midi.py" | awk '{print $2}' | xargs sudo kill
git pull
python midi.py