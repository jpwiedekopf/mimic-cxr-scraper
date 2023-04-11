#!/bin/bash

if [ ! -d .venv ]; then
  echo "create a new virtual environment using 'python -m venv .venv'!"
  echo "then, activate the venv with 'source .venv/bin/activate'!"
  exit 1
fi

pip install scrapy 
echo "You may need to install the 'MariaDB Connector/C' before installing the 'mariadb' pip package"
pip install mariadb 

printf "The following credentials can be left blank if you don't have them, but you will not be able to upload the data into the MariaDB database.\n"
printf "\nEnter MariaDB User\n"
read MARIADB_USERNAME
printf "\nEnter MariaDB Password (the password will not be echo-ed back, and not show up in your shell history!)\n"
read -s MARIADB_PASSWORD
printf "\nEnter MariaDB Host\n"
read MARIADB_HOST

# other vars: MARIADB_PORT (default 3306); MARIADB_DATABASE (default mimiciv)

printf "\nEnter Physionet User\n"
read PHYSIONET_USERNAME
printf "\nEnter Physionet Password (the password will not be echo-ed back, and not show up in your shell history!)\n"
read -s PHYSIONET_PASSWORD

cat <<EOF > .env
MARIADB_USERNAME="$MARIADB_USERNAME"
MARIADB_PASSWORD="$MARIADB_PASSWORD"
MARIADB_HOST="$MARIADB_HOST"

PHYSIONET_USERNAME="$PHYSIONET_USERNAME"
PHYSIONET_PASSWORD="$PHYSIONET_PASSWORD"
EOF