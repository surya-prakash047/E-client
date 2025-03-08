
# E-Client

A simple rule based email client capable of fetching mail and perform rule based actions




## Features

- Uses *Oauth* for authentication
- Integration of Gmail API
- Stores Email on a relational database (*Sqllite 3*)
- Performs certain rule based actions on fetched mails
- can label mails, make them read and unread




## Setup

**Configuration OAuth credentials**

- Login to [Google cloud](https://console.cloud.google.com)
- Create New project
- Enable Gmail API under API and credentials
- Create Oauth consent screen for credentials (desktop application)
- Download `client_secret.json` and store it in `./config/client_secret.json`
 
## Installation

1. Clone this repo

```bash
git clone https://github.com/surya-prakash047/E-client.git
cd E-client
```
2. Activate virtual environment
```bash
# Windows (ps)
python -m venv ./venv
./venv/Scripts/Activate.ps1
```
3. Install required libraries
```bash
pip install -r requirements.txt
```##Usage
After getting `client_secret.json` you can execute the main script by 
```bash
# Available args :- -c, --count, --display, --refresh, --mark-read, mark-unread
python main.py -c 20
```
**Using Streamlit interface**
For more ease of use you can run `stream_lit.py` 

```bash
streamlit run stream_lit.py
```
## Utils
you can run `recreate_db.py` to clear the database.

```bash
python recreate_db.py
```

### Screenshots    
![image](https://github.com/user-attachments/assets/50e8f8d2-5114-4353-8b20-d6e254314cd6)
