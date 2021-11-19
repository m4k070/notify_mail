# 未読メール通知スクリプト

## 概要

IMAP接続を行い、未読メールがあった場合SlackのIncoming Webhookに通知を行うスクリプトです。

## 設定

config.tomlに設定を記述します。

## 起動

### 直接実行

```
pip install poetry
poetry install
poetry run python ./notify.py
```

### docker-compose

```
docker-compose up -d
```