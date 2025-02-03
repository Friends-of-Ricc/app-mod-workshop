Self: https://github.com/Friends-of-Ricc/app-mod-workshop
Original code: [gdgpescara](https://github.com/gdgpescara/app-mod-workshop)

# TODO per Gregorio

1. Aggiungi `.env.dist`
1. Aggiungi `.env` a `.gitignore` per evitare che la gente lo checki per sbaglio.


## Ricc app

* App dev: `https://php-amarcord-dev-839850161816.europe-west8.run.app/`
* App prod: `https://php-amarcord-prod-839850161816.europe-west8.run.app/`
* Workshop links: `https://github.com/palladius/app-mod-workshop-set-by-step`

# Workshop: Application Modernization in GCP

Codebase for the workshop "Application Modernization in GCP"

This basic code will be used as base project for a workshop. *Important*: this is NSFW (Not Suitable For Work) and it should not be used as example in a production environment. The code might contain security issues and is not optimized for a Cloud environment. It is based on PHP5 and MySQL.

# Database initialization

You can initialize the database using the scripts in `/db`. `01_schema.sql` will create the database schema, `02_seed.sql` will populate the database with example data. It will insert 3 users:
* an Admin user, with `admin` as username and `admin123` as password;
* a normal User, with `user1` as username and `user123` as password;
* an other normal User, with `user2` as username and `user123` as password.
The database will also be populated with some images, that are already delivered with the application.

# Basic configuration

To configure the project:

* update `config.php` to reflect the parameters that will be used to connect to the MySQL db;
* make `/uploads` directory writable.
