# Python標準ライブラリ
import io
import os
import json
import logging
import urllib.request
import base64
import hashlib
import hmac

# Python外部ライブラリ
from fdk import response


def handler(ctx, data: io.BytesIO = None):

    # 定数定義
    REQUEST_URL = 'https://api.line.me/v2/bot/message/reply'
    LINE_CHANNEL_SECRET = os.environ['LINE_CHANNEL_SECRET']
    LINE_ACCESS_TOKEN = os.environ['LINE_ACCESS_TOKEN']
    DETECT_WORD = os.environ['DETECT_WORD']
    REQUEST_HEADERS = {
        'Authorization': 'Bearer ' + LINE_ACCESS_TOKEN,
        'Content-Type': 'application/json'
    }

    try:
        # リクエストの検証
        # data.getvalue()はBytes型
        request_body_bytes = data.getvalue()
        x_line_signature = ctx.Headers()['x-line-signature']    
        hashed_value = hmac.new(LINE_CHANNEL_SECRET.encode('utf-8'), request_body_bytes, hashlib.sha256).digest()
        signature = base64.b64encode(hashed_value)

        if signature != x_line_signature.encode(): 
            raise Exception("Discrepancies in signatures")

        for message_event in json.loads(request_body_bytes)['events']:
            # トークに投げられたメッセージがDETECT_WORDに一致するか判別する
            if DETECT_WORD == message_event['message']['text']:
                message = '検知ワードである「' + message_event['message']['text'] + '」が入力されたよ。'
            else:
                message = '「' + message_event['message']['text'] + '」は検知ワードではありません。'

            # 返信用のメッセージを作成
            body = {
                'replyToken': json.loads(request_body_bytes)['events'][0]['replyToken'],
                'messages': [
                    {
                        "type": "text",
                        "text": message,
                    }
                ]
            }
            request = urllib.request.Request(
                REQUEST_URL, 
                json.dumps(body).encode('utf-8'), 
                method='POST', 
                headers=REQUEST_HEADERS
            )
            with urllib.request.urlopen(request, timeout=10) as res:
                logging.getLogger().info('succuess')
    except (Exception, ValueError) as ex:
        logging.getLogger().info('Error message: ' + str(ex))
    return response.Response(
        ctx, response_data=REQUEST_URL,
        headers={"Content-Type": "application/json"}
    )
