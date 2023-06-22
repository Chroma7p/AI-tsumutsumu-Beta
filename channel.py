from dotenv import load_dotenv
from message import Message, Role
import os
import openai

REPLY_TOKEN = 1024

load_dotenv(".env")

SECRET_KEY = os.environ["SECRET_KEY"]

openai.api_key = os.environ["OPENAI_API_KEY"]
with open("./prompts/tsumugi_normal.txt", "r", encoding="utf-8") as f:
    TSUMUGI_PROMPT = f.read()

with open("./prompts/tsumugi_reply.txt", "r", encoding="utf-8") as f:
    TSUMUGI_REPLY = f.read()

TSUMUGI_PROMPT = TSUMUGI_PROMPT.replace("{SECRET_KEY}", SECRET_KEY)


def completion(history):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo-0613",
        messages=history,
        max_tokens=REPLY_TOKEN,
    )


class Mode:
    tsumugi = "tsumugi"
    chatgpt = "chatgpt"


class Channel:
    def __init__(self, channel_id, mode=Mode.tsumugi, is_temporary=False, unconditional=False, dajare=False):
        self.channelID = channel_id
        self.mode = mode

        self.base_prompt: list[Message] = [
            Message(Role.system, TSUMUGI_PROMPT),
            Message(Role.assistant, "こんにちは！あーしは埼玉ギャルの春日部つむぎだよ！"),
            Message(Role.user, "System:君のことを教えて！"),
            Message(
                Role.assistant, "あーしは埼玉県の高校に通う18歳のギャルで、身長155㎝だよ。誕生日は11月14日で、好きな食べ物はカレー。趣味は動画配信サイトの巡回だよ。"),
            Message(Role.user, "System:よろしくね！"),
            Message(Role.assistant, "よろしく！")
        ]
        self.history: list[Message] = []
        self.is_temporary = is_temporary
        self.reset()
        self.TOKEN_LIMIT = 4096
        self.unconditional = unconditional
        self.base_token = sum([x.token for x in self.base_prompt])
        self.dajare = dajare
        self.hiscore = 0

    def reset(self):
        self.history = []

    def set_unconditional(self, flag: bool):
        self.unconditional = flag

    def send(self, content: str, hash):
        if self.mode == Mode.tsumugi:
            new_content = TSUMUGI_REPLY.replace("{hash}", hash)
            new_content = new_content.replace("{content}", content)
            new_message = Message(Role.user, new_content)
            if new_message.token + self.get_now_token() + REPLY_TOKEN > self.TOKEN_LIMIT:
                self.thin_out(new_message.token)
            self.history.append(new_message)
            result = completion(self.make_log())
            content = content.replace(hash, "")
            self.history[-1] = Message(Role.system, content)

        else:
            self.history.append(Message(Role.user, content))
            result = completion(self.make_log())
        reply = result["choices"][0]["message"]["content"]
        self.history.append(Message(Role.assistant, reply))
        self.thin_out()
        return reply

    def make_log(self):
        if self.mode == Mode.tsumugi:
            return [hist.msg2dict() for hist in self.base_prompt + self.history]
        if self.mode == Mode.chatgpt:
            return [hist.msg2dict() for hist in self.history]

    def get_now_token(self, i=0):
        return sum([x.token for x in self.history]) + self.base_token

    def thin_out(self,new_token:int=0):  # 間引き
        now_token = self.get_now_token()
        remove_token = 0
        remove_index = 0
        while now_token - remove_token + new_token > self.TOKEN_LIMIT - REPLY_TOKEN:
            remove_token += self.history[remove_index].token
            remove_index += 1
        self.history = self.history[remove_index:]
