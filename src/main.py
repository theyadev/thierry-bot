from unidecode import unidecode

from os import getenv
from dotenv import load_dotenv

from readWords import readWordsJSON
from Enums import RedLetters, YellowLetters, BlueLetters
from Classes.game import Game, games
from utils import *

import interactions

load_dotenv()

DISCORD_TOKEN = getenv("DISCORD_TOKEN")

words, dict_words_accents = readWordsJSON("../public/words.json")

bot = interactions.Client(
    token=DISCORD_TOKEN, intents=interactions.Intents.ALL)


@bot.event
async def on_ready():
    print("HELLO WORLDOU")


@bot.command(
    name="start",
    description="Start a game of Motus",
    options=[
        interactions.Option(
            name="difficulty",
            description="The difficulty of the word",
            required=True,
            type=interactions.OptionType.STRING,
            choices=[
                interactions.Choice(name="Easy", value="easy"),
                interactions.Choice(name="Medium", value="medium"),
                interactions.Choice(name="Hard", value="hard")
            ]
        )
    ]
)
async def start(ctx: interactions.CommandContext, difficulty: str = "medium"):
    if doesGameExist(games, ctx.channel_id):
        await ctx.send("Il y a deja une partie en cours !", ephemeral=True)
        return

    random_word = getRandomWordByDifficulty(words, difficulty)

    game = Game(ctx.channel_id, random_word)

    game.setRandomCorrectLetters(2)

    channel = await ctx.get_channel()

    await ctx.send(f"Démarrage de la partie. Mo Mo Motus !\nEntrez un mot de {len(random_word)} lettres")

    await channel.send(game.correctLettersToString())


@bot.command(
    name="test",
    description="Send a test word with his definition",
    options=[
        interactions.Option(
                name="difficulty",
                description="The difficulty of the word",
                required=True,
                type=interactions.OptionType.STRING,
                choices=[
                    interactions.Choice(name="Easy", value="easy"),
                    interactions.Choice(name="Medium", value="medium"),
                    interactions.Choice(name="Hard", value="hard")
                ]
        ) 
    ]
)
async def test(ctx: interactions.CommandContext, difficulty: str = "medium"):
    random_word = getRandomWordByDifficulty(words, difficulty)

    random_word_accent = dict_words_accents.get(random_word)

    embed = generateEmbed(
        f"Le mot de test est: {random_word_accent}", random_word_accent, bot.me.icon_url)

    await ctx.send(embeds=embed, ephemeral=True)


@bot.command(
    name="stop",
    description="Stop a game of Motus",
)
async def stop(ctx: interactions.CommandContext):
    if not doesGameExist(games, ctx.channel_id):
        await ctx.send("Il n'y a pas de partie en cours")
        return

    game = games.get(ctx.channel_id)

    game.delete()

    await ctx.send("Partie terminée !")


@bot.event()
async def on_message_create(message: interactions.Message):
    msg = unidecode(message.content).lower()

    # Pass message by bot
    if message.author.id == bot.me.id:
        return

    # Pass message if no active games in channel
    if not games.get(message.channel_id):
        return

    random_word = games.get(message.channel_id).word

    # Pass if the length of the word is not the same as the random_word
    if len(msg) != len(random_word):
        return

    if not msg in words:
        return await message.reply("Le mot que vous avez écrit n'est pas français.")

    game = games.get(message.channel_id)

    # Create a list with every valid letters
    list_letters = list(random_word)

    # [-, -, -, -, -, -]
    result = [BlueLetters.EMPTY for i in range(len(random_word))]

    # Set all correctly placed letters
    for i, letter in enumerate(msg):
        # If letter is correctly placed
        if letter == random_word[i]:
            # Remove letter from list
            index = list_letters.index(letter)
            list_letters.pop(index)

            # Replace - with valid letter

            letter_append = RedLetters[letter]

            game.correct[i] = letter_append
            result[i] = letter_append

        else:
            result[i] = BlueLetters[letter]

    # Set all letters not correctly placed
    for i, letter in enumerate(msg):
        # If letter is in the list of correct letters
        if letter in list_letters:
            # If letter is already placed continue
            if type(result[i]) != BlueLetters:
                continue

            # Remove letter from list
            index = list_letters.index(letter)
            list_letters.pop(index)

            # Replace - with incorrectly placed letter
            result[i] = YellowLetters[letter]

    historique = game.history
    historique.append(result)

    game.current += 1

    if len(historique) > 2:
        historique.pop(0)

    channel = await message.get_channel()

    await channel.send(game.historyToString())

    if msg == game.word:
        game.delete()
        # TODO: Embed
        phrase = getRandomPhrase(message.author)

        embed = generateEmbed(phrase, dict_words_accents.get(
            game.word), message.author.avatar_url)

        return await channel.send(embeds=embed)

    if game.current >= game.limit:
        embed = generateEmbed(f"Partie terminée ! Le mot était: {game.word}", dict_words_accents.get(
            game.word), bot.me.icon_url)
        await channel.send(embeds=embed)
        game.delete()

bot.start()
