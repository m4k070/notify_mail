import email
import imaplib
import json
import ssl
import time
import urllib.parse
import urllib.request
from email.header import decode_header
from email.message import EmailMessage
from email.message import Message
from typing import Any, List, MutableMapping

import toml

def getSubjectStr(msg: Message) -> str:
    #print(msg["Subject"])
    (bytes, encoding), *_ = decode_header(msg["Subject"])
    if type(bytes) is str:
        return bytes
    if encoding:
        subjectstr: str = bytes.decode(encoding)
        return subjectstr
    else:
        subjectstr: str = bytes.decode('utf-8')
        return subjectstr

def main():
    conf: MutableMapping[str, Any] = toml.load("config.toml")["mail"]
    user: str = conf["user"]
    password: str = conf["password"]
    interval: int = conf["interval"]
    notify_numbers: List[str] = []  # 通知済みメッセージNoリスト

    print("start")

    while True:
        imap: imaplib.IMAP4 = None
        try:
            if conf["use_ssl"] == True:
                imap = imaplib.IMAP4_SSL(host=conf["server"], port=conf["port"])
            else:
                context = ssl.create_default_context()
                imap = imaplib.IMAP4(host=conf["server"], port=conf["port"])
                imap.starttls(ssl_context=context)

            imap.login(user, password)
            imap.select()

            print("check")
            type, data = imap.search(None, "UNSEEN")
            s = str.split(data[0].decode())
            numbers = [num for num in s if not (num in notify_numbers)]

            notify_messages: List[str] = []
            for num in numbers:
                print(f"before fetch({num})")
                _, msgdata = imap.fetch(num, "(RFC822)")
                print("complete fetch")
                _, _ = imap.store(num, "-FLAGS", "\\Seen")
                msgstr = msgdata[0][1].decode()
                #print(f"msgstr:{msgstr}")
                msg: Message = email.message_from_string(msgstr)
                subjectstr: str = getSubjectStr(msg)
                notify_messages.append(subjectstr)
            print(notify_messages)
        except Exception:
            print("server connection error")
            time.sleep(1)
            continue
        finally:
            # 切断
            if imap:
                imap.close()
                imap.logout()

        if len(numbers) > 0:
            postUrl: str = conf["hook_url"]

            post_text = "未読メールがあります。\n"
            post_text = post_text + "\n".join(notify_messages)

            postdata: str = json.dumps(
                {
                    "text": post_text,  # 通知内容
                    "username": "Mail Checker",  # ユーザー名
                    "icon_emoji": ":smile_cat:",  # アイコン
                    # "link_names": 1,  # 名前をリンク化
                }
            )
            postbyte: bytes = postdata.encode("UTF-8")
            request: urllib.request.Request = urllib.request.Request(postUrl, postbyte)
            response = urllib.request.urlopen(request)
            print(response.getcode())
            html = response.read()
            print(html.decode("utf-8"))
            notify_numbers.extend(numbers)

        time.sleep(interval)


if __name__ == "__main__":
    main()
