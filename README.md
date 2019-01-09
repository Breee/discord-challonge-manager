# discord-challonge-manager

# Setup
## 1. Requirements: 
- python3
- pip3
- discord bot user (https://discordapp.com/developers/applications/me)

## 2. Install discord.py and numpy:
```
pip3 install -r requirements.txt
```

## 3. Configuration:
Copy the file `config.ini.example` to `config.ini` (or create it). 
The configuration file is of the form: 

```
[bot]
token = <bot_token>
playing = u mom lel

[discord]
admin_roles = ["role_id1","role_id2"]
manager_roles = ["role_id3","role_id4"]

[challonge]
api_key = xyz
user_name = someone
```



## 4. Starting the bot
Call:
```
python3 start_bot.py
```
