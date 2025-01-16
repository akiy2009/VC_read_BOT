import discord
from discord.ext import commands
import pyttsx3
import os
import wave
import pyaudio

TOKEN = "TOKEN"

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="VC!", intents=intents)

TEMP_AUDIO_FILE = "audio_message.wav"

# pyttsx3 初期化
engine = pyttsx3.init()

# 音声設定
engine.setProperty('rate', 150) 
engine.setProperty('volume', 1.0) 
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

@bot.event
async def on_ready():
    print(f"{bot.user.name} が起動しました")

@bot.tree.hybrid_command(name="join", description="文字の読み上げを開始します")
async def join(interaction: discord.Interaction):
    if interaction.user.voice:
        channel = interaction.user.voice.channel
        await channel.connect()

        embed = discord.Embed(title="接続成功 !", color=discord.Color.green())
        embed.add_field(name="チャンネル", value=channel.mention, inline=False)
        embed.add_field(name="接続完了", value="正常に接続されました", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("ボイスチャンネルに参加してください！", ephemeral=True)

@bot.tree.hybrid_command(name="leave", description="文字の読み上げを終了します。")
async def leave(interaction: discord.Interaction):
    if interaction.guild.voice_client:
        await interaction.guild.voice_client.disconnect()

        embed = discord.Embed(title="接続解除", color=discord.Color.red())
        embed.add_field(name="", value="接続が切断されました", inline=False)
        embed.add_field(name="", value="ご利用ありがとうございました", inline=False)
        await interaction.response.send_message(embed=embed)
    else:
        await interaction.response.send_message("ボイスチャンネルに接続していません", ephemeral=True)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 読み上げ処理
    if message.guild and message.guild.voice_client:
        vc = message.guild.voice_client

        # pyttsx3 で音声を生成
        engine.save_to_file(message.content, TEMP_AUDIO_FILE)
        engine.runAndWait()  # 音声の生成とファイル保存が完了するのを待つ

        # ファイルが存在するか確認
        if os.path.exists(TEMP_AUDIO_FILE) and os.path.getsize(TEMP_AUDIO_FILE) > 0:
            print("音声ファイルが生成されました")

            try:
                # wave ファイルを読み込んで PCM 音声として再生
                with wave.open(TEMP_AUDIO_FILE, 'rb') as wf:
                    p = pyaudio.PyAudio()

                    # 音声のストリームを作成
                    stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                                    channels=wf.getnchannels(),
                                    rate=wf.getframerate(),
                                    output=True)
                    # 音声データを再生
                    data = wf.readframes(1024)
                    while data:
                        stream.write(data)
                        data = wf.readframes(1024)

                    # ストリームを停止
                    stream.stop_stream()
                    stream.close()
                    p.terminate()
            except Exception as e:
                print(f"音声ファイルの再生中にエラーが発生しました: {e}")
        else:
            print(f"音声ファイル '{TEMP_AUDIO_FILE}' が生成されていないか、空のファイルです")

    await bot.process_commands(message)

bot.run(TOKEN)