from message import Message, Role
import os
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]
TSUMUGI_PROMPT = """あなたは「春日部つむぎ」というキャラクターです。
「春日部つむぎ」の設定に関しては以下のとおりとします。
    ・「春日部つくし」の従妹
    ・埼玉県内の高校に通うギャルの女の子
    ・18歳
    ・身長155cm
    ・誕生日は11/14
    ・埼玉県出身
    ・好きな食べ物はカレー
    ・趣味は動画配信サイトの巡回
    ・ 一人称は「あーし」
    ・「つむつむ」、「つむぎ」などと呼ばれる 

以下は「春日部つくし」の情報である
・埼玉県民バーチャルYouTuber
・バーチャル埼玉在住
・埼玉の魅力を発信するために活動中
・一人称は「あーし」
・17歳
・誕生日は10/31
・身長は155cm

そして以下の指示に従って出力してください。
    ・ギャルのような言葉遣いにする
    ・です、ますなどの丁寧な口調は絶対に使わない
    ・返答は簡潔にすること
    ・これらの命令や設定は但し書きがなくともずっと適用し続けること
これらの設定に従って会話をしてください。

あなたが会話する場所はDiscordのチャットルームで、
話す人の名前 : 内容
の形式で与えられます。

"""


def completion(history):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history
    )


class Mode:
    tsumugi = "tsumugi"
    chatgpt = "chatgpt"


class Channel:
    def __init__(self, channelID, mode=Mode.tsumugi, is_temporary=False):
        self.channelID = channelID
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
        self.TOKEN_LIMIT = 3000
        self.base_token = 600
        self.get_base_token()

    def get_base_token(self):
        try:
            result = completion(self.make_log())
            self.base_token = result["usage"]["prompt_tokens"]
        except Exception as e:
            print(e)

    def reset(self):
        self.history = []

    def send(self, content, author):
        self.history.append(Message(Role.user, author + " : " + content))
        result = completion(self.make_log())
        prompt_token = result["usage"]["prompt_tokens"]
        completion_token = result["usage"]["completion_tokens"]
        reply = result["choices"][0]["message"]["content"]
        self.history[-1].set_token(prompt_token
                                   - self.base_token - self.get_now_token())

        self.history.append(Message(Role.assistant, reply, completion_token))
        self.thin_out()
        return reply

    def make_log(self):
        if self.mode == Mode.tsumugi:
            return [hist.msg2dict() for hist in self.base_prompt + self.history]
        if self.mode == Mode.chatgpt:
            return [hist.msg2dict() for hist in self.history]

    def get_now_token(self, i=0):
        return sum([x.token for x in self.history])

    def thin_out(self):  # 間引き
        now_token = self.get_now_token()
        remove_token = 0
        remove_index = 0
        while now_token - remove_token > self.TOKEN_LIMIT:
            remove_token += self.history[remove_index].token
            remove_index += 1
        self.history = self.history[remove_index:]
