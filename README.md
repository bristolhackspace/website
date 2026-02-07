# Bristol Hackspace website

The website is built using Flask and uses mosparo spam detection for forms.

A blog section is provided using content authored in a Django CMS that is available at this [repository](https://github.com/bristolhackspace/website-django-cms).

## Prerequisites

To run this code locally it is assumed you have installed:

- git
- pyenv (to allow selection of virtual python environments)
- pip

## Running Locally

### Clone the repo

```bash
git clone https://github.com/bristolhackspace/website.git

cd website
```

### Create example config file

This is a one-off config, if you already created the file you can skip this step.

```bash
mkdir instance
cd instance
cat << 'EOF' > config.toml
#Fake
MOSPARO_ENABLED = false
MOSPARO_HOST="localhost"
MOSPARO_PUBLIC_KEY="0x000"
MOSPARO_PRIVATE_KEY="0x001"
MOSPARO_UUID="12345"
SECRET_KEY='01234567890'
AWS_ACCESS_KEY_ID='<AWS_ACCESS_KEY_ID>'
AWS_SECRET_ACCESS_KEY='<AWS_SECRET_ACCESS_KEY>'
AWS_STORAGE_BUCKET_NAME='<garage-bucket-name>'
AWS_S3_ENDPOINT_URL='http://127.0.0.1:3900'
AWS_S3_REGION_NAME='garage'
PUBLIC_MEDIA_URL="http://127.0.0.1:5000/media/"
EOF
```

Verify the contents of the config.toml

```bash
cat config.toml
```

Note: The AWS credentials are required for files that are hosted in a garage bucket.  These updates allow the Hackspace website to reach out to a garage bucket for images that are added in a blog article.

### Set virtual environment

Ensure you are in the project root and create a virtual environment.

Select a Python 3.11 version, first check what versions are installed:

```bash
pyenv versions
  system
  3.10.13
* 3.11.8 (set by /Users/username/.pyenv/version)
  3.12.2
```

Install a Python 3.11 version if one is not listed:

```bash
pyenv local 3.11.8
python --version
```

create the virtual environment:

```bash
python -m venv .venv

# Activate it (macOS/Linux)
source .venv/bin/activate

# or on Windows PowerShell
# .venv\Scripts\Activate.ps1

# Update pip
pip install --upgrade pip
```

### Install the project

From the project root:

```bash
pip install -r requirements.txt
```

### Configure Flask environment variables

```bash
# On macOS/Linux (bash/zsh)
export FLASK_APP=hackspace_website:create_app
export FLASK_ENV=development

# On Windows PowerShell
# $env:FLASK_APP = "hackspace_website:create_app"
# $env:FLASK_ENV = "development"
```

### Run the development server

Check you are in the root of the project.

```bash
flask run

 * Serving Flask app 'hackspace_website:create_app'
 * Debug mode: off
WARNING: This is a development server. Do not use it in a production deployment. Use a production WSGI server instead.
 * Running on http://127.0.0.1:5000
```

With the server running, in a browser navigate to: http://127.0.0.1:5000
