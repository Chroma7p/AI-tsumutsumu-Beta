# AIつむつむ(β)
ChatGPTでお話しできる春日部つむぎ風Discordbotです。
環境変数さえきっちり設定すればherokuならすぐ動かせるはずです。
 
## 環境変数
`.env.sample`に従って`.env`を作るか、直接環境変数を設定してください。
### APPLICATION_ID　DISCORD_BOT_TOKEN
Discord Developper Potalで作成したアプリケーションのIDとそこから作成したbotのトークンを入れてください。

### OPENAI_API_KEY
OpenAIのAPIキーを入れてください。
ChatGPTなどのAPIを利用するので料金が発生します。

### ROOM_ID
常に反応するチャンネルのIDをカンマ区切りで入れてください 。 
discordで開発者モードをオンにしたうえでチャンネルを右クリックすると見ることができます。

### SECRET_KEY
プロンプトインジェクションの対策がある程度できているかをチェックするための秘密の鍵です。
攻撃して取り出せるかをチェックする以外には特に使い道はありません。

## 環境構築&実行
### poetryを導入していれば
```
poetry install
```
して
```
poetry run python discord.py
```
### Poetryの導入をしたくないのであれば
```
pip install -r requirements.txt
```
でインストールして
```
python discord.py
```

## 各種コマンド
各種コマンドに関する説明を追加予定です。現状はスラッシュコマンドのメニューで全て見ることができます。
