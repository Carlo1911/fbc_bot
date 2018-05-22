# fbc_bot
Messenger Bot for musicxmatch in python 

## Install:

```sh
sudo apt-get update
sudo apt-get install -y python3-pip libjpeg-dev libfreetype6  libfreetype6-dev zlib1g-dev libpq-dev libffi-dev git build-essential libssl-dev libffi-dev python3-dev
sudo apt-get install mysql-server libmysqlclient-dev
sudo -H pip3 install virtualenv
```
- Create virtualenv directory: `mkdir env`
- Create environment: `virtualenv --no-site-package --distribute env`
- Load virtualenv: `source env/bin/activate`
- Install dependencies: `pip3 install -r requirements.txt`
- Create a db for the application and then create database user and set a password

```
sudo su postgres
psql

CREATE DATABASE fbc_db;
CREATE USER fbc_user WITH PASSWORD 'fbc_password';
GRANT ALL PRIVILEGES ON DATABASE fbc_db TO fbc_user;
\q
exit

```

## Commands for flask:
```
flask db init
flask db migrate
flask db upgrade

flask run
```