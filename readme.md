![](logo.png)

Designet for å funke på Raspberry Pi OS.

Krever at du registrer en bot/app i Slack for å få `SLACK_APP_TOKEN` og `SLACK_BOT_TOKEN`. Se en [guide her](https://docs.slack.dev/apis/events-api/using-socket-mode/). Appen krever `connections:write` som Slack admins må godkjenne.


Installer: 

```bash
sudo apt-get install wtype cvlc firefox

python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Start manuelt:
```bash
python kakebot.py 
```

Start automatisk: (log blir skrevet til kakebot.log i prosjektet)
```bash
(crontab -l 2>/dev/null; echo "@reboot cd $(pwd) && $(pwd)/.venv/bin/python kakebot.py >> $(pwd)/kakebot.log 2>&1") | crontab -
```

For å slette cronjob rediger bort linjen nederst i `crontab -e` eller kill midlertidlig med `pkill -f kakebot.py`

