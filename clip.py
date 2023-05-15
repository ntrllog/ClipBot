import discord, os
from moviepy.editor import *

output_file = 'clipped_by_clip_bot.mp3'

def clip_the_video(input_file, start_time, end_time):
    # read input video file using moviepy
    video = VideoFileClip(input_file)
    
    start_time = max(start_time, 0)
    end_time = min(end_time, video.duration)

    # extract audio from video between start and end times
    audio = video.audio.subclip(start_time, end_time)

    # write extracted audio to output file
    audio.write_audiofile(output_file, verbose=False, logger=None)

    # close the video and audio objects
    video.close()
    audio.close()

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')
    await client.change_presence(activity=discord.Game(name='Type [clip] for help'))

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('[clip]'):
        if message.content == '[clip]':
            await message.channel.send(embed=displayHelp())
            return

        if message.reference is None:
            await message.channel.send('You gotta reply to a video in the chat! Dummy!')
            return

        try:
            content = message.content.split(' ')
            start_time = content[1]
            end_time = False
            if len(content) > 2:
                end_time = content[2]
            if not start_time.isnumeric():
                await message.channel.send('The start time has to be a number! Dummy!')
                return
            if end_time and not end_time.isnumeric():
                await message.channel.send('The end time has to be a number! Dummy!')
                return

            reply_msg = await message.channel.fetch_message(message.reference.message_id)

            path_to_video = reply_msg.content
            if reply_msg.attachments:
                path_to_video = reply_msg.attachments[0].url

            start_time = int(start_time)
            if end_time == False:
                end_time = start_time + 5
            end_time = int(end_time)
            clip_the_video(path_to_video, start_time, end_time)

            path_to_clipped_video = os.path.join(os.getcwd(), output_file)
            await message.channel.send(file=discord.File(path_to_clipped_video))
        except Exception as e:
            print(e)
            await message.channel.send(e)

def displayHelp():
    text = '''reply to a video with [clip] start_time end_time
    for example, [clip] 3 6
    will clip the video from 00:03 to 00:06
    discord's soundboard only allows 5-second sounds
    so if you put an end_time that's too high
    the bot will stop at start_time + 5
    if you don't wanna put an end time then
    the bot will stop at start_time + 5
    '''
    embed = discord.Embed(title='For Dummies', color = 0x00ff00)
    embed.add_field(name='Commands', value=text, inline=False)
    return embed

client.run(os.getenv('CLIENT_TOKEN'))