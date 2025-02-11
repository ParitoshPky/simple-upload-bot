from telethon import TelegramClient, events
from download_from_url import download_file
from config import BOTTOKEN, APIID, APIHASH, DOWNLOADPATH, USERNAME
import os
import time
import datetime
import asyncio
import aiohttp
from utils import progress, humanbytes, time_formatter, convert_from_bytes
import traceback
import speedtest
import requests

bot = TelegramClient('upbot', APIID, APIHASH).start(bot_token=BOTTOKEN)

def get_date_in_two_weeks():
    """
    get maximum date of storage for file
    :return: date in two weeks
    """
    today = datetime.datetime.today()
    date_in_two_weeks = today + datetime.timedelta(days=14)
    return date_in_two_weeks.date()
"""
async def send_to_transfersh_async(file):
    
    size = os.path.getsize(file)
    size_of_file = humanbytes(size)
    final_date = get_date_in_two_weeks()
    file_name = os.path.basename(file)

    print("\nUploading file: {} (size of the file: {})".format(file_name, size_of_file))
    
    url = 'https://api.anonfiles.com/upload/'
 
    with open(file, 'rb') as f:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={str(file): f}) as response:
                    download_link = await response.text()              
    print("Link to download file(will be saved till {}):\n{}".format(final_date, download_link))
    return download_link, final_date, size_of_file
    
    with open(file, 'rb') as f:
        callapi = requests.post("https://api.anonfiles.com/upload", data={str(file): f})
        text = callapi.json()
    return text, final_date, size_of_file
""" 

async def upload_file(ufile):
    """This function uploads the given
    file to anonfiles."""
    
    with open(ufile, mode='rb') as file_handler:
        r = requests.post('https://api.anonfiles.com/upload', files={'file': file_handler})
    
    return r.json()['data']['file']['url']['full']

"""
def uploaded_file_info(fileid):
    This function gives information 
    about the file on anonefiles.
    r = requests.get(f'https://api.anonfiles.com/v2/file/{fileid}/info')
    data = r.json()['data']['file']['metadata']
    try:
        fid = data['id']
    except:
        fid = None
    try:
        fname = data['name']
    except:
        fname = None
    try:
        fbsize = data['size']['bytes']
    except:
        fbsize = None
    try:
        frsize = data['size']['readable']
    except:
        frsize = None
    return f'''File ID: {fid}\nFile Name: {fname}\nFile Size (in bytes): {fbsize}\nFile Size (readable): {frsize}'''
"""


async def send_to_tmp_async(file):
    url = 'https://tmp.ninja/api.php?d=upload-tool'
    
    with open(file, 'rb') as f:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data={"file": f}) as response:
                    download_link =  await response.text()
                    
    return download_link


@bot.on(events.NewMessage(pattern='/start'))
async def start(event):
    """Send a message when the command /start is issued."""
    await event.respond('Hi! please send me any file url or file uploaded in Telegram and I will upload to Telegram as file or generate download link of that file. Also you can upload sent file to TransferSh / TmpNinja.')
    raise events.StopPropagation

@bot.on(events.NewMessage(pattern='/up'))
async def up(event):
    if event.reply_to_msg_id:
        start = time.time()
        url = await event.get_reply_message()
        ilk = await event.respond("Downloading...")
        
        try:
            filename = os.path.join(DOWNLOADPATH, os.path.basename(url.text))
            file_path = await download_file(url.text, filename, ilk, start, bot)
        except Exception as e:
            print(e)
            await event.respond(f"Downloading Failed\n\n**Error:** {e}")
        
        await ilk.delete()

        try:
            orta = await event.respond("Uploading to Telegram...")

            dosya = await bot.upload_file(filename, progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, orta, start, "Uploading to Telegram...")
                ))

            zaman = str(time.time() - start)
            await bot.send_file(event.chat.id, dosya, force_document=True, caption=f"{filename} uploaded in {zaman} seconds! By {USERNAME}")
        except Exception as e:
            traceback.print_exc()

            print(e)
            await event.respond(f"Uploading Failed\n\n**Error:** {e}")
        
        await orta.delete()

    raise events.StopPropagation
"""   
@bot.on(events.NewMessage(pattern='/anonup'))
async def tsh(event):
    if event.reply_to_msg_id:
        start = time.time()
        url = await event.get_reply_message()
        orta = await event.respond("Uploading to TransferSh...")
        data, pfile, purl, full = await upload_file(url)
        zaman = str(time.time() - start)
        await orta.edit(f"File Successfully Uploaded to TransferSh.\n\nLink:{full}\nFile:{pfile}")
    raise events.StopPropagation
    
"""
@bot.on(events.NewMessage(pattern='/transfersh'))
async def tsh(event):
    if event.reply_to_msg_id:
        start = time.time()
        url = await event.get_reply_message()
        ilk = await event.respond("Downloading...")
        try:
            file_path = await url.download_media(progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, ilk, start, "Downloading...")
                ))
        except Exception as e:
            traceback.print_exc()
            print(e)
            await event.respond(f"Downloading Failed\n\n**Error:** {e}")
        
        await ilk.delete()
    if event.reply_to_msg_id:
        start = time.time()
        url = await event.get_reply_message()
        ilk = await event.respond("Downloading...")
        
        try:
            filename = os.path.join(DOWNLOADPATH, os.path.basename(url.text))
            file_path = await download_file(url.text, filename, ilk, start, bot)
        except Exception as e:
            print(e)
            await event.respond(f"Downloading Failed\n\n**Error:** {e}")
        
        await ilk.delete()


        try:
            orta = await event.respond("Uploading to TransferSh...")
            newdata = await upload_file(file_path)

            zaman = str(time.time() - start)
            await orta.edit(f"File Successfully Uploaded to TransferSh.\n\nLink:{newdata}")
        except Exception as e:
            traceback.print_exc()
            print(e)
            await event.respond(f"Uploading Failed\n\n**Error:** {e}")

    raise events.StopPropagation
    

@bot.on(events.NewMessage(pattern='/speedtest'))
async def speedtest(event):
    ilk = await event.respond(f"Calculating my internet speed. Please wait!")
    start = time.time()
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download()
    s.upload()
    end = time.time()
    ms = (end - start).microseconds / 1000
    response = s.results.dict()
    download_speed = response.get("download")
    upload_speed = response.get("upload")
    ping_time = response.get("ping")
    client_infos = response.get("client")
    i_s_p = client_infos.get("isp")
    i_s_p_rating = client_infos.get("isprating")
    await ilk.edit("""**SpeedTest** completed in {} seconds
        Download: {}
        Upload: {}
        Ping: {}
        Internet Service Provider: {}
        ISP Rating: {}""".format(ms, convert_from_bytes(download_speed), convert_from_bytes(upload_speed), ping_time, i_s_p, i_s_p_rating))

    raise events.StopPropagation
@bot.on(events.NewMessage(pattern='/tmpninja'))
async def tmp(event):
    if event.reply_to_msg_id:
        start = time.time()
        url = await event.get_reply_message()
        ilk = await event.respond("Downloading...")
        try:
            file_path = await url.download_media(progress_callback=lambda d, t: asyncio.get_event_loop().create_task(
                    progress(d, t, ilk, start, "Downloading...")
                ))
        except Exception as e:
            traceback.print_exc()
            print(e)
            await event.respond(f"Downloading Failed\n\n**Error:** {e}")
        
        await ilk.delete()

        try:
            orta = await event.respond("Uploading to TmpNinja...")
            download_link = await send_to_tmp_async(file_path)

            zaman = str(time.time() - start)
            await orta.edit(f"File Successfully Uploaded to TmpNinja.\n\nLink:{download_link}")
        except Exception as e:
            traceback.print_exc()
            print(e)
            await event.respond(f"Uploading Failed\n\n**Error:** {e}")

    raise events.StopPropagation



def main():
    if not os.path.isdir(DOWNLOADPATH):
        os.mkdir(DOWNLOADPATH)

    """Start the bot."""
    print("\nBot started..\n")
    bot.run_until_disconnected()

if __name__ == '__main__':
    main()
