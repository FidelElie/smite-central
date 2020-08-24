# SMITE Central
A Website For Your Smite Needs.

## Setup
### The Python Environment
First start by creating a virtual python environment.
```powershell
python -m venv venv
```
This will create a directory "*venv*" in your working directory. Then you should activate
by running:
```bash
source "venv/scripts/activate"
```
On Unix systems and
```powershell
.\venv\Scripts\activate
```
On Windows Systems.

Now that we have activated the python environment, we can install all
the current dependencies for the application by using the *requirments.txt* file. This is
achieved by the command:

```powershell
pip install -r requirements.txt
```
If we were to run this application now we will get an error, the python environment is completed
so now we have to configure the django environment.
### The Django Environment
The application is set to choose what settings it will load in during runtime using an environment
variable. By default if the **DJANGO_SETTINGS_MODULE** environment variable is not set, the development
environment will be chosen "*smitecentral.settings.development*".

During development api keys and other credentials are read from a *credentials.json* file. As you
will see there is no such file in the repository as this will be created by you and remain exempt from version control. This file should be placed in the root directory i.e where the README.md and manage.py files are located.

Keys To Provide Are:
* **SECRET_KEY**: Secret key for django application can be anything.
* **YOUTUBE_API_KEY**: API key for YouTube data api.
* **POSTGRES_PASSWORD**: Password for your local postgres server, *NOTE the name of the database is set to smitecentral, if you want a different name you could also define this key in the credentials file.*

Next let run database migrations using the command:

```powershell
python manage.py migrate
```
We can now run the application using the command:
```powershell
python manage.py runserver
```
Happy hacking.

### Deployment
In Deployment environment variables are set on the server themselves (e.g Config Vars on the Heroku
platform). We do not want the development environment to be used so we define the environment variable:

``` powershell
DJANGO_SETTINGS_MODULE = smitecentral.settings.production
```

This will cause django to run production settings on the webserver. Ensure this is set before the code
is pushed.

Additionally, if you want to test the website in a production environment, the *production_local* file
can be used to test, error pages etc. To show this set:

```jsonc
{
    // other keys and credentials
    "DJANGO_SETTINGS_MODULE": "smitecentral.settings.production_local"
}
```
in your *credentials.json* file.

# Acknowledgements
* Django for their framework and documentation.
* HiRez and Titanforge for making a great game with amazing art.
* The players who make every game exciting to watch no matter the league.
