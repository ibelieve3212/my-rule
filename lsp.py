import os
import re
import json
import random
import asyncio
from pathlib import Path
from telethon import utils, functions
from telethon.tl.types import PeerChannel, InputMessagesFilterPhotos, InputMessagesFilterVideo, InputMessagesFilterUrl, InputMediaPhotoExternal

def get_prefix():
    config_path = Path(__file__).resolve().parent.parent / 'config/config.json'
    with config_path.open() as f:
        config = json.load(f)
        return config.get('prefix', '#')

prefix = get_prefix()

required = ['requests']

command = 'lsp'
shortDescription = 'lsp'
longDescription = '''
可用参数：`mjx`、`album`、`video`、`slide`
配置文件：`TMBdata/config/lsp.json`
配置参考：
```{
    "mjx": "https://mjx.xxxxx.xxx/",
    "album": [
        "https://t.me/ch_anne_l"
    ],
    "video": [
        "https://t.me/ch_anne_l"
    ],
    "slide": [
        "https://t.me/ch_anne_l"
    ]
}
```
'''
type = 'cmd'
filename = os.path.basename(__file__)

config_path = Path(__file__).resolve().parent.parent / 'config/lsp.json'

default_config = { 
  'mjx': '', 
  'album': [''],
  'video': [''],
  'slide': ['']
}

if not config_path.exists():
    config_path.write_text(json.dumps(default_config, indent=4))

async def handle(event):
    await event.delete()
    import requests

    message = event.message.message.split()
    cmd = message[1] if len(message) > 1 and message[1] in ['mjx', 'album', 'video', 'slide'] else random.choice(['mjx', 'album', 'video', 'slide'])

    with config_path.open() as f:
        config = json.load(f)
        mjx = config.get('mjx', False)
        album = config.get('album', False)
        video = config.get('video', False)
        slide = config.get('slide', False)

    async def send_mjx():
        if not mjx:
            await event.respond(f'请先设置配置文件，参考:\n{longDescription}')
        try:
            with requests.Session() as s:
                r = s.get(mjx)
            if r.ok:
                url = r.json()['url']
                caption = r.json()['des']
                await event.respond(f'\n[买家秀：]({url})\n__{caption}__')
        except:
            await event.respond('获取失败...')

    async def send_album():
        if not album:
            await event.respond(f'请先设置配置文件，参考:\n{longDescription}')
        peer = await event.client.get_entity(random.choice(album))

        for _ in range(5):
            count = (await event.client.get_messages(peer, filter=InputMessagesFilterPhotos)).total
            random_offset = random.randint(1, count)
            album_messages = []

            async for msg in event.client.iter_messages(peer, offset_id=random_offset, limit=1, filter=InputMessagesFilterPhotos):
                if msg.grouped_id:
                    async for m in event.client.iter_messages(peer, offset_id=(random_offset + 10), limit=20, filter=InputMessagesFilterPhotos):
                        if msg.grouped_id == m.grouped_id:
                            album_messages.append(m.id)
            if album_messages:
                await event.client(functions.messages.ForwardMessagesRequest(
                    from_peer=peer,
                    id=album_messages,
                    to_peer=event.message.peer_id,
                    with_my_score=True,
                    drop_author=True,
                    drop_media_captions=True,
                    noforwards=True
                ))
                return
        await event.respond('获取失败~')

    async def send_video():
        if not video:
            await event.respond(f'请先设置配置文件，参考:\n{longDescription}')
        peer = await event.client.get_entity(random.choice(video))
        for _ in range(5):
            count = (await event.client.get_messages(peer, filter=InputMessagesFilterVideo)).total
            random_offset = random.randint(1, count)
            async for m in event.client.iter_messages(peer, offset_id=random_offset, filter=InputMessagesFilterVideo):
                await event.client(functions.messages.ForwardMessagesRequest(
                    from_peer=peer,
                    id=[m.id],
                    to_peer=event.message.peer_id,
                    with_my_score=True,
                    drop_author=True,
                    drop_media_captions=True,
                    noforwards=True
                ))
                return
        await event.respond('获取失败~')

    async def send_slide():
        if not slide:
            await event.respond(f'请先设置配置文件，参考:\n{longDescription}')
        peer = await event.client.get_entity(random.choice(slide))
        for _ in range(5):
            count = (await event.client.get_messages(peer, filter=InputMessagesFilterUrl)).total
            random_offset = random.randint(1, count)
            url = title = img_urls = ''
            async for m in event.client.iter_messages(peer, offset_id=random_offset, limit=1, filter=InputMessagesFilterUrl):
                url = m.web_preview.url
                title = m.web_preview.title

            if url:
                res = requests.get(url)
                img_urls = re.findall(r'<img [^>]*src="([^"]+)"[^>]*', res.text)

            if img_urls and title:
                if not (img_urls[0].startswith('http://') or img_urls[0].startswith('https://')):
                    img_urls = ['https://telegra.ph/' + str(i) for i in img_urls]

                msg = await event.respond(message=title, file=InputMediaPhotoExternal(url=img_urls[0]))
                del img_urls[0]
                for i, photo in enumerate(img_urls):
                    if i < len(img_urls):
                        await asyncio.sleep(5)
                        msg_exists = await event.client.get_messages(event.message.peer_id, ids=msg.id)
                        if msg_exists:
                            await msg.edit(text=title, file=InputMediaPhotoExternal(url=img_urls[i]))
                        else:
                            return
            return
        await event.respond('获取失败~')

    tasks = {
        "mjx": send_mjx,
        "album": send_album,
        "video": send_video,
        "slide": send_slide,
    }

    if cmd in tasks:
        await tasks[cmd]()

