import json
import time
import logging
import routes
import requests
from dotenv import dotenv_values

config = dotenv_values(".env")

TOKEN = config["BOT_TOKEN"]


def main():
    last_update_id = None
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

    headers = {
        "accept": "application/json",
        "content-type": "application/json"
    }
    while True:
        payload = {
            "offset": last_update_id,
            "limit": None,
            "timeout": None
        }
        r = requests.post(url, json=payload, headers=headers)
        command_list = r.json()["result"]
        for command in command_list:
            if "callback_query" in command:
                logging.info("Callback query: " + json.dumps(command["callback_query"]["message"]))
                routes.callback_query(command)
            elif "message" in command:
                if "entities" in command["message"] and (command["message"]["entities"][0]["type"] == 'bot_command'):
                    logging.info("Bot command: " + json.dumps(command["message"]))
                    routes.commands(command)
                else:
                    logging.info("Input text: " + json.dumps(command["message"]))
                    routes.input_text(command)
            else:
                logging.critical("Unknown command: " + command)
        if len(command_list) != 0:
            last_update_id = command_list[-1]["update_id"] + 1
        print(last_update_id)
        time.sleep(0.4)


if __name__ == '__main__':
    logging.basicConfig(filename="log.txt",
                        level=logging.INFO,
                        format="%(asctime)s %(message)s",
                        filemode="w")
    main()
