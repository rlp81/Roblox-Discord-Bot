import discord
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
import logging
import json
import ngrok
import configparser
import threading
from discord.ext import commands, tasks
guildids = [0] # ADD YOUR GUILD/SERVER ID HERE
conf = configparser.ConfigParser()
confile = conf.read("config.conf")
auth = str(conf.get("config", "auth"))
token = str(conf.get("config", "token"))
tun = str(conf.get("config", "tunnel"))
psw = str(conf.get("config", "password"))
url = "https://"+tun

bot = discord.Bot(debug_guilds=[guildids])

format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")


class Query:

    def __init__(self):
        self.queue = {'auth': 'deny', 'queue': {}}
        self.active = []
        self.bot = []

    def fetch_queue(self):
        return self.queue["queue"]

    def add_queue(self, server, item, value):
        if not server in self.queue["queue"]:
            self.queue["queue"][server] = {}
        self.queue["queue"][server][item] = value

    def remove_queue(self, server):
        if server in self.queue["queue"]:
            del self.queue["queue"][server]

    def reset_queue(self):
        self.queue = {'auth': 'deny', 'queue': {}}

    def fetch_active(self):
        return self.active

    def add_active(self, item):
        self.active.append(item)

    def remove_active(self, item):
        if item in self.active:
            self.active.remove(item)

    def reset_active(self):
        self.active = []

    def fetch_bot(self):
        return self.bot

    def add_bot(self, item):
        self.bot.append(item)

    def remove_bot(self, item):
        if item in self.active:
            self.bot.remove(item)

    def reset_bot(self):
        self.bot = []


lib = Query()

@tasks.loop(seconds=10)
async def bot_queue():
    queue = lib.fetch_bot()
    if queue != []:
        for i in queue:
            if 'channel' in i:
                chan = await bot.fetch_channel(int(i['channel']))
                if chan:
                    if 'message' in i:
                        await chan.send(i['message'])
        lib.reset_bot()



class ReqHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        data = {'key': 'value'}
        body = bytes(json.dumps(data), "utf-8")
        self.protocol_version = "HTTP/1.1"
        self.send_response(200)
        self.send_header("Content-Length", len(body))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        info = self.rfile.read(int(self.headers['Content-Length']))
        rec = info.decode('utf8')
        res = json.loads(rec)
        send = {}
        if 'password' in res and res['password'] == psw and 'server' in res:
            if "start" in res:
                lib.add_active(res['start'])
            elif 'stop' in res:
                lib.remove_active(res['stop'])
            server = res['server']
            if 'queue' in res:
                for x in res['queue']:
                    lib.add_bot(x)
            queue = lib.fetch_queue()
            if not server in queue:
                queue = {}
            else:
                queue = queue[server]
            send = {
                'auth': 'allow',
                "queue": queue
            }
        else:
            send = {'auth':'deny', "queue": {}}
        body = bytes(json.dumps(send), "utf-8")
        self.protocol_version = "HTTP/1.1"
        self.send_response(200)
        self.send_header("Content-Type", 'application/json')
        self.end_headers()
        self.wfile.write(body)
        lib.reset_queue()


def tunnel():
    logging.info("Starting tunnel...")
    ngrok.set_auth_token(auth)
    lis = ngrok.forward(1233, domain=tun)
    logging.info(f"Ingress established at {lis.url()}")
    time.sleep(1)
    server()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info("Closing connection")
        ngrok.disconnect(tun)


def server():
    server = HTTPServer(("localhost", 1233), ReqHandler)
    logging.info("Starting server")
    server.serve_forever()


@bot.command()
async def send_global_message(ctx: discord.ApplicationContext, msg):
    await ctx.respond(f"Adding message {msg} to queue")
    act = lib.fetch_active()
    que = {
        'message': msg
    }
    queue = lib.fetch_queue()
    for i in act:
        if i in queue:
            num = 1
            for x in queue[i]:
                num += 1
            lib.add_queue(i, num, que)
        else:
            lib.add_queue(i, 1, que)


@bot.event
async def on_ready():
    logging.info(f"Logged in as {bot.user}")
    bot_queue.start()
    threading.Thread(target=tunnel).start()


bot.run(token)
