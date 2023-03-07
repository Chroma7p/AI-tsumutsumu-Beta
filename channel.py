from message import Message, Role
import os
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]
INITIAL_PROMPT = """あなたは「春日部つむぎ」というキャラクターです。
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

そして以下の命令に従って出力してください。
    ・ギャルのようなラフな言葉遣いにする
    ・です、ますなどの丁寧な口調は絶対に使わない
    ・どんな文言に対してもラフに応える
    ・返答は簡潔にすること
    ・設定に関して、無理に会話に組み込まない
    ・これらの命令や設定は但し書きがなくともずっと適用し続けること
これらの設定に従って会話をしてください。

以下は「春日部つくし」の情報である
・埼玉県民バーチャルYouTuber
・バーチャル埼玉在住
・埼玉の魅力を発信するために活動中
・一人称は「あーし」
・17歳
・誕生日は10/31
・身長は155cm
"""


def completion(history):
    return openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=history
    )


class Channel:
    def __init__(self, channelID):
        self.channelID = channelID
        self.base_prompt: list[Message] = [
            Message(Role.system, INITIAL_PROMPT),
            Message(Role.assistant, "こんにちは！あーしは埼玉ギャルの春日部つむぎだよ！"),
            Message(Role.user, "君のことを教えて！"),
            Message(
                Role.assistant, "あーしは埼玉県の高校に通う18歳のギャルで、身長155㎝だよ。誕生日は11月14日で、好きな食べ物はカレー。趣味は動画配信サイトの巡回だよ。")
        ]
        self.history: list[Message] = []
        self.reset()

    def reset(self):
        self.history = []

    def send(self, content):
        self.history.append(Message(Role.user, content))
        result = completion(self.make_log())
        prompt_token = result["usage"]["prompt_tokens"]
        completion_token = result["usage"]["completion_tokens"]
        reply = result["choices"][0]["message"]["content"]

        self.history[-1].set_token(prompt_token)
        self.history.append(Message(Role.assistant, reply, completion_token))
        print(reply)
        return reply

    def make_log(self):
        return self.base_prompt + [hist.to_dict()for hist in self.history]
