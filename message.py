class Role:
    user = "user"
    system = "system"
    assistant = "assistant"


class Message:
    def __init__(self, role: Role, content: str, token: int = 0):
        self.role = role
        self.content = content
        self.token = 0

    def msg2dict(self) -> dict:
        return {"role": self.role, "content": self.content}

    def set_token(self, token):
        self.token = token
