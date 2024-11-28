#!/bin/bash

source ~/miniconda3/bin/activate
conda activate gs-chatbot

exec hypercorn -c hypercorn.toml src/app:app
