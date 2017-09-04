from discord    import Client, User, Object
from redis      import from_url, StrictRedis
from time       import time
from os         import getenv
import pickle
import asyncio


DISCORD_BOT_KEY = gentenv('DISCORD_TOKEN')
DISCORD_CHANNELS = [241014195884130315]
REDIS_URL = getenv('REDIS_URL')
TIMER = 24 # hours
RESET_ON_LOAD = False


class RedisDict():
    def __init__(self, redis, redis_key, data={}):
        if type(data) is not dict:
            raise TypeError
        self.data = data
        self.redis = redis
        self.redis_key = redis_key

    def save(self):
        data = pickle.dumps(self.data)
        self.redis.set(self.redis_key, data)

    def load(self):
        data = self.redis.get(self.redis_key)
        if data is None:
            self.data = {}
        else:
            self.data = pickle.loads(data)

async def check_timers(delay=60):
    await client.wait_until_ready()

    while not client.is_closed:
        users.load()
        for user_id, user_time in users.data.items():
            time_left = TIMER * 3600 + user_time - time()

            if time_left < 0:
                del users.data[user_id]
                users.save()
                for chan_id in DISCORD_CHANNELS:
                    channel = Object(id=chan_id)
                    user = await client.get_user_info(user_id)
                    await client.send_message(channel, "The timer of %s is finished !" % user.name)
                await client.send_message(user, "Your timer is finished! It has been removed.")

        await asyncio.sleep(delay)


client = Client()
redis = from_url(REDIS_URL)
users = RedisDict(redis=redis, redis_key='users')

@client.event
async def on_message(message):
    if message.content.startswith('!timer'):
        users.load()

        if message.content == '!timer':
            if message.author.id not in users.data:
                users.data[message.author.id] = time()
                users.save()
                await client.send_message(message.author, "Started a %s hours timer just for you!" % TIMER)
            else:
                time_left = TIMER * 3600 + users.data[message.author.id] - time()
                hours = time_left // 3600
                mins = time_left % 3600 // 60
                await client.send_message(message.author, "You have {h:.0f}:{m:.0f} left.".format(h=hours, m=mins))

        else:
            if message.content.startswith('!timer reset'):
                if message.author.id in users.data:
                    del users.data[message.author.id]
                    users.save()
                    await client.send_message(message.author, "Your timer was sucessfully removed.")
                else:
                    await client.send_message(message.author, "You have no timer set yet! Perhaps it has finished?")

            elif message.content.startswith('!timer list'):
                msg = "Running timers:"
                if users.data == {}:
                    msg += "\n    No timers set yet."
                else:
                    for user_id, user_time in users.data.items():
                        time_left = TIMER * 3600 + user_time - time()
                        hours = time_left // 3600
                        mins = time_left % 3600 // 60
                        user = await client.get_user_info(user_id)
                        msg += "\n    {u.name}: {h:.0f}:{m:.0f} left".format(u=user, h=hours, m=mins)
                await client.send_message(message.channel, "```%s```" % msg)

            elif message.content.startswith('!timer help'):
                await client.send_message(message.channel, "```Skywanderers timer help:\n    !timer\n    !timer reset\n    !timer list\n    !timer help```")

            else:
                await client.send_message(message.channel, "Unknown command `%s`. Please see `!timer help`." % message.content)

@client.event
async def on_ready():
    print("Logged in as {u.name} ({u.id}).".format(u=client.user))
    if RESET_ON_LOAD:
        users.save()
        print("Data reinit done.")
    try:
        users.load()
        print("Data loading sucessful.")
    except NameError:
        print("Error occured while loading data. Attempting to reinit.")
        users.save()
        print("Data reinit done.")

client.loop.create_task(check_timers(60))
client.run(DISCORD_BOT_KEY)
