# Commander Doch 1 Telegram Bot
> Welcome to join in and feel free to contribute.

## Features

 - Auto send report on specific date
 - Auto send reports by default
 - Change soldier's status on a specific date
 - Change soldier's default status
 - Show future config
 - Send today's Doch1
 
## To be impelemnted
 - More statuses
 - Edit note on 'Outside base' status
 - Cookies cache file

## How to use
 1. clone the repository
 2. copy "config.json.example" to "config.json" in the same directory
 3. edit config.json (with your personal data), more details [here](#example-configuration-file)
 4. Install python-telegram-bot by using the following pip command: pip install python-telegram-bot==12.0.0b1 --upgrade
 5. run from command line: `python3 bot.py`

## Example Configuration file
```
{
	"telegram_api_key": "587285866:jWBJbmaD_dHvVijV_ixJLmEcPEwUUgXsFg3",
	"telegram_chat_id": "445364189",
	"password": "264759062",
	"username": "034408997",
	"cookies": {
		"incap_ses_264_2025883": "",
		 "visid_incap_2025883": "",
		 "AppCookie": "",
		 "BIGipServerMFT-One-Frontends": "",
		 "nlbi_2025883": ""
		}
}

```


In order to use this script, you must create your own bot on telegram. You can find more information on the subject here: [telegram bots introduction](https://core.telegram.org/bots)