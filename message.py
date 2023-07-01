from enum import Enum
import tiktoken


class Role(Enum):
    system = "system"
    user = "user"
    assistant = "assistant"


class Message:
    """
    メッセージのクラス
    メッセージごとにロールと内容とトークンを保持する
    """

    def __init__(self, role: Role, content: str, token: int = 0):
        self.role: Role = role
        self.content: str = content
        self.calc_token()

    def msg2dict(self) -> dict:
        return {"role": self.role.name, "content": self.content}

    def set_token(self, token: int) -> None:
        self.token = token

    def msg2str(self) -> str:
        return f"{self.role.name} : {self.content}"

    def __str__(self) -> str:
        return self.msg2str()

    def calc_token(self):
        """Returns the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model("gpt-3.5-turbo-0613")
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")

        self.token = len(encoding.encode(self.content))
