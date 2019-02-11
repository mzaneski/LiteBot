#python 3.6.7

import discord

import asyncio
import datetime
import random

OWNER_ID = '' #optional id for whoever is hosting the bot to allow admin commands
BOT_TOKEN = '' #bot token provided by discord

BALL_ANSWERS = ['It is certain',
                'It is decidedly so.',
                'Without a doubt.',
                'Yes. Definitely.',
                'You may rely on it.',
                'As I see it, yes.',
                'Most likely.',
                'Outlook good.',
                'Yes.',
                'Signs point to yes.',
                'Don\'t count on it.',
                'My reply is no.',
                'My sources say no.',
                'Outlook is not so good.',
                'Very doubtful.']

def command(admin_only=False, **m_kwargs):
    def wrap(func):
        async def deco(bot, message, *args, **kwargs):
            if message.channel.is_private:
                return
            if deco.admin_only:
                chk1 = not message.author.server_permissions.administrator
                chk2 = not message.author.id == OWNER_ID
                if chk1 and chk2:
                    return

            await func(bot, message, *args, **kwargs)

        setattr(deco, 'admin_only', admin_only)

        for k in m_kwargs:
            setattr(deco, k, m_kwargs[k])

        return deco
    return wrap

@command()
async def listcmds(bot, message, **kwargs):
    """Lists all commands.
    """

    cmds = 'USER COMMANDS:\n'
    cmds_admin = '\nADMIN COMMANDS:\n'
    for cmd in bot.commands:
        w = ''
        try:
            h = getattr(bot.commands[cmd], 'help_str')
        except:
            h = ''
        if bot.commands[cmd].admin_only:
            cmds_admin += (bot.command_prefix + cmd + ' ' + h + w + '\n')
        else:
            cmds += (bot.command_prefix + cmd + ' ' + h + w + '\n')
        
    await bot.send_message(message.channel, '```' + cmds + cmds_admin + '```')

@command(admin_only=True, allow_whitelist=False, help_str='<single char>')
async def prefix(bot, message, split_text=[''], **kwargs):
    """Changes the prefix for commands.
    """

    try:
        if len(split_text[1]) > 1:
            raise IndexError
        bot.command_prefix = split_text[1]
    except IndexError:
        await bot.send_message(message.channel, 'Invalid arguments. Proper usage: {}prefix <single char>'.format(bot.command_prefix))
    except ValueError:
        await bot.send_message(message.channel, 'Invalid arguments. Choose a different character')
    else:
        await bot.send_message(message.channel, 'Bot command prefix changed to {}'.format(bot.command_prefix))

@command(admin_only=True, help_str='<nickname>')
async def nickme(bot, message, split_text=[''], **kwargs):
    """Changes the bot nickname on the server.
    """

    try:
        await bot.change_nickname(message.server.me, ' '.join(split_text[1:]))
    except IndexError:
        await bot.send_message(message.channel, 'Invalid arguments. Proper usage: {}nickme <nickname>'.format(bot.command_prefix))
    except:
        await bot.send_message(message.channel, 'Unknown error')

@command(help_str='<min(optional)> <max> (default: 0, 100)')
async def roll(bot, message, split_text=[''], **kwargs):
    """Rolls a random number.
    The first and last number provided are the min and max, respectively.
    If the max is 1 then a random float between 0.0 and 1.0 is rolled.
    """

    random.seed()
    minroll = 0
    maxroll = 100
    prev = minroll

    if split_text[1:]:
        for arg in split_text[1:]:
            if arg.isdigit():
                if int(arg) > prev:
                    maxroll = int(arg)
                    minroll = prev
                prev = int(arg)

    if maxroll == 1:
        await bot.send_message(message.channel, random.random())
    else:
        await bot.send_message(message.channel, random.randrange(minroll, maxroll + 1))

@command()
async def coin(bot, message, **kwargs):
    """Heads or tails.
    """

    random.seed()
    await bot.send_message(message.channel, 'heads') if bool(random.getrandbits(1)) else await bot.send_message(message.channel, 'tails')

@command(help_str='<username>')
async def blame(bot, message, split_text=[''], **kwargs):
    """Pings somebody in the server and blames them. Very annoying and fun.
    """

    try:
        member = None
        if len(split_text[1]) >= 3:
            member = discord.utils.find(lambda x: x.display_name.lower().find(split_text[1]) != -1, message.server.members)

        if member is None:
            if split_text[1].lower().startswith(('me', 'myself')):
                blamed = 'you'
            elif split_text[1].find(bot.owner_id) != -1 or split_text[1].find(message.server.me.id) != -1:
                blamed = 'everyone but myself'
            else:
                blamed = ' '.join(split_text[1:])
        elif member.id in (bot.owner_id, message.server.me.id):
            blamed = 'everyone but myself'
        elif member.id == message.author.id:
            blamed = 'you'
        else:
            blamed = '<@{}>'.format(member.id)
    except:
        await bot.send_message(message.channel, '...')
    else:
        await bot.send_message(message.channel, 'Personally,\nI blame {}'.format(blamed))

@command(help_str='<question>')
async def ball(bot, message, **kwargs):
    """Obligatory 8ball command.
    """

    random.seed()
    if message.content.find('sandwich') != -1:
        reply = BALL_ANSWERS[random.randrange(11, len(BALL_ANSWERS))]
    elif message.content.find('|') != -1:
        reply = 'Did you perhaps mean to say {}choose? :o)'.format(bot.command_prefix)
    else:
        reply = BALL_ANSWERS[random.randrange(len(BALL_ANSWERS))]

    await bot.send_message(message.channel, reply)

@command(help_str='<choice1 | choice2 | etc...> (max: 10)')
async def choose(bot, message, split_text=[''], **kwargs):
    """Chooses a random option from the choices provided to it.
    """

    choices = []
    tmp = ' '.join(split_text[1:]).split('|')

    for t in tmp:
        if not t.isspace() and t not in choices:
            choices.append(t.strip())

    if len(choices) > 1 and len(choices) <= 10:
        random.seed()
        await bot.send_message(message.channel, '\"{}\"'.format(choices[random.randrange(len(choices))]))
    else:
        await bot.send_message(message.channel, "Invalid input. Proper usage: {}choose <choice1 | choice2 | etc...> (max: 10)".format(bot.command_prefix))

@command(help_str='<string>')
async def spam(bot, message, split_text=[''], **kwargs):
    """Converts ASCII letters into discord emojis.
    """

    emojis = []

    for word in split_text[1:]:
        for c in word:
            dec = ord(c)
            if c == '\n':
                emojis.append('\n')
            elif c == ' ':
                emojis.append('  ')
            elif dec == 98:
                emojis.append(':b:')
            elif dec > 96 and dec < 123:
                emojis.append(':regional_indicator_' + chr(dec) + ':')
            elif dec > 47 and dec < 58:
                if dec == 48:
                    emojis.append(':zero:')
                elif dec == 49:
                    emojis.append(':one:')
                elif dec == 50:
                    emojis.append(':two:')
                elif dec == 51:
                    emojis.append(':three:')
                elif dec == 52:
                    emojis.append(':four:')
                elif dec == 53:
                    emojis.append(':five:')
                elif dec == 54:
                    emojis.append(':six:')
                elif dec == 55:
                    emojis.append(':seven:')
                elif dec == 56:
                    emojis.append(':eight:')
                else:
                    emojis.append(':nine:')
            elif dec == 33:
                emojis.append(':exclamation:')
            elif dec == 63:
                emojis.append(':question:')

    response = ''.join(emojis)
    if response and not response.isspace():
        await bot.send_message(message.channel, response)

class LiteBot(discord.Client):

    def __init__(self, owner_id, bot_token):
        super().__init__(max_messages=100)

        self.owner = owner_id
        self.token = bot_token
        
        self.command_prefix = '!'

        self.commands = {}
        self.commands['listcmds'] = listcmds
        self.commands['prefix'] = prefix
        self.commands['nickme'] = nickme
        self.commands['roll'] = roll
        self.commands['coin'] = coin
        self.commands['blame'] = blame
        self.commands['ball'] = ball
        self.commands['choose'] = choose
        self.commands['spam'] = spam
    
    def run(self):
        super().run(self.token)

    async def on_ready(self):
        print('Bot logged in successfully.' + datetime.datetime.now().strftime("%H:%M %m-%d-%Y"))
        print(self.user.name)
        print(self.user.id)

    async def on_message(self, message):
        if message.content and message.content[0] == self.command_prefix:
            content = message.content.split(' ')
            if content[0][1:] in self.commands:
                await self.commands[content[0][1:]](self, message, split_text=content)

    async def on_member_remove(self, member):
        n = '<@{}>\nRIP: {} ({})'.format(member.server.owner.id, member.display_name, member.name)
        lived = '\nBorn ' + member.joined_at.strftime("%H:%M %m-%d-%Y")
        died = '\nDied ' + datetime.datetime.now().strftime("%H:%M %m-%d-%Y")

        await self.send_message(member.server.default_channel, n + lived + died)

if __name__ == '__main__':
    cl = LiteBot(OWNER_ID, BOT_TOKEN)  
    cl.run()
