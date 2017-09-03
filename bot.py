from discord import Client, User, Object
from redisworks import Root
from time import time
import asyncio

DISCORD_BOT_KEY = 'MzUzNzA1OTIxNjE4MTE2NjA5.DIzl1A.jwiFMZ63i_D9jn4k31whkVqPw6c'
DISCORD_CHANNELS = [241014195884130315]
REDIS_LOGIN = {
    host: 'localhost',
    port: 6379,
    db: 0
}
TIMER = 24 # hours
RESET_ON_LOAD = False


def reset():
    storage.users = {}

async def check_timers(delay=60):
    await client.wait_until_ready()

    while not client.is_closed:
        for user_id, user_time in storage.users.items():
            time_left = time() + TIMER - user_time

            if time_left < 0:
                del storage.users[user_id]
                for chan_id in DISCORD_CHANNELS:
                    channel = Object(id=chan_id)
                    user = User(id=user_id)
                    await client.send_message(channel, "The timer of %s is finished !" % user.name)
                await client.send_message(user, "Your timer is finished! It has been removed.")

        await asyncio.sleep(delay)


storage = Root(**REDIS_LOGIN)
client = Client()

@client.event
async def on_message(message):
    if message.content.startswith('!timer'):

        if message.content == '!timer':
            if message.author.id not in storage.users:
                storage.users[message.author.id] = time()
                await client.send_message(message.author, "Started a %s hours timer just for you!" % TIMER)
            else:
                time_left = time() + TIMER - storage.users[message.author.id]
                hours = time_left // 3600
                mins = time_left % 3600 // 60
                await client.send_message(message.author, "You have %s:%s time left." % (hours, mins))

        else:
            if message.content.startswith('!timer reset'):
                if message.author.id in storage.users:
                    del storage.users[message.author.id]
                    await client.send_message(message.author, "Your timer was sucessfully removed.")
                else:
                    await client.send_message(message.author, "You have no timer set yet! Perhaps it has finished?")

            if message.content.startswith('!timer list'):
                msg = "Running timers:"
                for user_id, user_time in storage.users.items():
                    time_left = time() + TIMER - user_time
                    hours = time_left // 3600
                    mins = time_left % 3600 // 60
                    user = User(id=user_id)
                    msg += "\n    {u.name}: {h}:{m} left".format(u=user, h=hours, m=mis)
                else:
                    msg += "\n    No timers set yet."
                await client.send_message(message.channel, "```%s```" % msg)

            elif message.content.startswith('!timer help'):
                await client.send_message(message.channel, "```Skywanderers timer help:\n    !timer\n    !timer reset\n    !timer list\n    !timer help```")

            else:
                await client.send_message(message.channel, "Unknown command `%s`. Please see `!timer help`." % message.content)

@client.event
async def on_ready():
    print("Logged in as {u.name} ({u.id}).".format(u=client.user)
    if RESET_ON_LOAD or storage.users is None:
        reset()
        print("Data reinit done.")

client.loop.create_task(check_timers(60))
client.run(DISCORD_BOT_KEY)
