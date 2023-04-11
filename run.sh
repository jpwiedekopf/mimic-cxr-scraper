#!/bin/bash

if [ ! -d .venv ]; then
  echo "run the ./prepare-env script"
  exit 1
fi

activate () {
  . .venv/bin/activate
}

activate
touch ./data.jsonl
out_file=$(realpath data.jsonl)


scrapy crawl physionet -O $out_file
