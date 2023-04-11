# mimic-cxr-scraper

To use the script, you will need to be a credentialed user on https://physionet.net and have access to the [MIMIC-CXR dataset](https://physionet.org/content/mimic-cxr/2.0.0/).

first create a python virtual env with:

```bash
python -m venv .venv
```

Then, run the `prepare-env.sh` script, which will write a hidden file `.env` with the credentials (and install requirements as needed):

```bash
./prepare-env.sh
```

Afterwards, run the `run.sh` script.

```bash
./run.sh
```

This will scrape the TXT files into a `ndjson` file `data.jsonl` in your working directory, and, if configured, upload the data into the configured MariaDB database.
