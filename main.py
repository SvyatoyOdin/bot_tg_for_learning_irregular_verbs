import requests, json, os, datetime, time
from dotenv import load_dotenv

load_dotenv()
TOKEN = f'https://api.telegram.org/bot{os.getenv("token")}/'
CHAT_ID = os.getenv('chat_id')


def get_irregular_verbs() -> dict:
    with open('irregular_verbs.json', 'r') as file:
        return json.load(file)


def update_file(object) -> None:
    with open('irregular_verbs.json', 'w') as file:
        json.dump(object, file, ensure_ascii=False, indent=4)


def send_message(text: str) -> None:
    data = {"chat_id": CHAT_ID, "text": text}
    requests.post(f'{TOKEN}sendmessage', data=data)
    time.sleep(0.3)  # waiting not to spam telegram server, otherwise it is returning incorrect information


def delete_message(message_id: int) -> None:
    data = {'chat_id': CHAT_ID, 'message_id': message_id}
    requests.post(f'{TOKEN}deletemessage', data=data)
    time.sleep(0.3)  # waiting not to spam telegram server, otherwise it is returning incorrect information


def check_time_to_send_message(time_send_message) -> bool:
    # ste( time ).split('.')[0] - takes away milliseconds
    if str(time_send_message).split('.')[0] == str(datetime.datetime.now()).split('.')[0]:
        if datetime.datetime.now().hour >= 10:
            return True


def await_answer(update_id) -> list:
    while True:
        response = requests.get(f'{TOKEN}getupdates').json()
        if response['result'][-1]['update_id'] != update_id:
            update_id = response['result'][-1]['update_id']
            text = response['result'][-1]['message']['text']
            message_id = response['result'][-1]['message']['message_id']
            return [update_id, text, message_id]
        time.sleep(0.4)  # waiting not to spam telegram server, otherwise it is returning incorrect information


def main() -> None:
    re = requests.get(f'{TOKEN}getupdates').json()
    time.sleep(0.3)
    if re['result']:
        update_id = re['result'][-1]['update_id']
        time_send_message = datetime.datetime.now()
        while True:
            if check_time_to_send_message(time_send_message):
                russion_word_and_irregular_verbs: dict = get_irregular_verbs()

                repetitions: int = russion_word_and_irregular_verbs['repetitions']
                russion_word: str = list(russion_word_and_irregular_verbs)[1]
                irregular_verbs: str = russion_word_and_irregular_verbs[russion_word]

                send_message(text=russion_word)
                while True:
                    update_id, user_answer, message_id = await_answer(update_id)
                    if irregular_verbs == user_answer.lower():
                        if repetitions < 18:
                            send_message(text='right')

                            russion_word_and_irregular_verbs['repetitions'] += 1

                            update_file(russion_word_and_irregular_verbs)
                            delete_message(message_id)
                        else:
                            send_message(text='you have learned a new word')

                            russion_word_and_irregular_verbs.pop(russion_word)
                            russion_word_and_irregular_verbs['repetitions'] = 0

                            update_file(russion_word_and_irregular_verbs)
                        break
                    else:
                        send_message(text='wrong, try again')
                        delete_message(message_id)

                time_send_message = datetime.datetime.now() + datetime.timedelta(hours=1)


if __name__ == '__main__':
    main()
