import os
import requests
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from dotenv import load_dotenv

load_dotenv()

print("Starter kake bot app...")
SLACK_BOT_TOKEN = os.getenv("SLACK_BOT_TOKEN")
SLACK_APP_TOKEN = os.getenv("SLACK_APP_TOKEN")

if not SLACK_BOT_TOKEN or not SLACK_APP_TOKEN:
    raise ValueError("SLACK_BOT_TOKEN og SLACK_APP_TOKEN må være satt i .env fil eller environment.")

print(f"SLACK_APP_TOKEN={SLACK_APP_TOKEN[:30]}...")
print(f"SLACK_BOT_TOKEN={SLACK_BOT_TOKEN[:30]}...")

SKJERM_TIMEOUT_SEKUNDER = 160
print(f"Skjerm timeout er satt til {SKJERM_TIMEOUT_SEKUNDER} sekunder")

KAKELYD = "cookie.mp3"
print(f"Kakelyd fil er satt til \"{KAKELYD}\"")

TILLAT_LISTE = ["kake"]
MAX_TEXT_LENGDE = 250
print("Filtrerer meldinger med:")
print(f"Maks tekst lengde {MAX_TEXT_LENGDE} tegn")
print(f"Må ha bilde eller inkludere ord {TILLAT_LISTE}")

@dataclass
class Melding:
    text: str
    image_url: Optional[str]
    file_name: str = field(init=False)

    def __post_init__(self):
        self.file_name = download_image(self, SLACK_BOT_TOKEN)

    def er_kake(self):
        innhold = self.text.lower()
        tillat = any(ord in innhold for ord in TILLAT_LISTE)
        return (self.image_url or tillat) and len(innhold) < MAX_TEXT_LENGDE

def download_image(melding: Melding, token):
    if melding.image_url:
        try:
            file_name = f"image.{melding.image_url.split('.')[-1]}"
            response = requests.get(melding.image_url, headers={"Authorization": f"Bearer {token}"})
            if response.status_code == 200:
                with open(file_name, "wb") as f:
                    f.write(response.content)
                return file_name
        except:
            pass
    return ""

def generer_html(melding: Melding, html_navn = "index.html"):
    with open("template.html", "r", encoding="utf-8") as f:
        template = f.read()

    with open(html_navn, "w", encoding="utf-8") as f:
        f.write(template.replace("{ TEKST }", melding.text).replace("{ BILDE }", melding.file_name or "ingen_bilde.jpg"))
    
    return html_navn

def aktiver_kakebot(melding: Melding):
    print("Aktiverer kakebot...")
    html_navn = generer_html(melding)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.system(f'(sleep 2 && cvlc --intf dummy --play-and-exit --gain 5 {script_dir}/{KAKELYD})&')
    os.system(f'(firefox --new-tab "file://{script_dir}/{html_navn}")&')
    os.system(f'(sleep {SKJERM_TIMEOUT_SEKUNDER} && wtype -M ctrl w -m ctrl)&')

slack_app = App(token=os.getenv("SLACK_BOT_TOKEN"))

@slack_app.event("message")
def handle_message_events(body, logger):
    event = body.get("event", {})
    text = event.get("text", "")
    is_thread = event.get("thread_ts", None) is not None
    image_url = event.get("files", [{}])[0].get("url_private", "")
    melding = Melding(text=text, image_url=image_url)
    print(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}: Mottatt melding: \"{text[:100]}\", bilde_url: \"{image_url}\", thread: {is_thread}, er_kake: {melding.er_kake()}")

    if not is_thread and melding.er_kake():
        aktiver_kakebot(melding)

def start_slack_app():
    try:
        SocketModeHandler(slack_app, SLACK_APP_TOKEN).start()
    except:
        pass

def main():
    start_slack_app()


if __name__ == "__main__":
    main()