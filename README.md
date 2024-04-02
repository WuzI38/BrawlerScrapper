# BrawlerScrapper
![example workflow](https://github.com/WuzI38/BrawlerScrapper/actions/workflows/ci.yml/badge.svg)

This project aims to collect data on Magic: The Gathering (MTG) decks in the Brawl format using the services of aetherhub.com and mtgdecks.net.

## Requirements

- Python 3.10 or higher

## Scripts

- `run.py`: This script adds to the database the decks created on the current day.
- `app/fill_database.py`: This script initializes the database using a portion of the decks registered on the services that were created in the last 3 years.

## Database

The project requires an SQL database to function properly. A script for creating the database (`db_create.sql`) will be included in the repository.

## Configuration

To connect to the database, a configuration file (`config.ini`) needs to be created in the `config` directory in the main project directory. Here is an example of what the configuration file should look like:

```
[database]
user = root
password = root
name = Brawler
host = localhost
```
