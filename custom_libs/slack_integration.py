from slacker import Slacker

API_KEY = "xxxx-xxxxxxxxxxxx-xxxxxxxxxxxxxxxxxxxxxxxx"
CHANNEL = "#career-intelligence-platform"

slack = Slacker(API_KEY)


def send_slack(message):
    slack.chat.post_message(CHANNEL, message)


if __name__ == '__main__':
    send_slack("TEST!")
