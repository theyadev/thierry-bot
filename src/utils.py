import requests

from random import choice
from bs4 import BeautifulSoup

import interactions


def doesGameExist(games, id):
    curr_game = games.get(id, None)

    if curr_game is None:
        return False

    return True


def enumsToString(enum_list):
    return " ".join(map(lambda l: l.value, enum_list))


def getRandomWordByDifficulty(words, difficulty: str):
    filter_enum = difficulty_filters[difficulty]

    filtered_words = list(filter(filter_enum, words))

    random_word = choice(filtered_words)

    return random_word


def getRandomPhrase(user):
    if user.id == 346417942575185922:
        return "Wow bravo Mélanie tu es vraiment très forte, ça me fait très plaisir que tu joues à mon jeu."

    phrases = [
        f"Bravo {user.username}, tu as trouvé le mot.",
        f"C'est presque trop facile pour toi {user.username}, bravo.",
        f"Tu as trouvé le mot, mais tu as eu de la chance {user.username}.",
        f"{user.username} a trouvé la réponse ! Mo Mo Motus !",
        f"Bravo {user.username}, tu es un champion !"
    ]

    return choice(phrases)


def scrapDefinition(url: str) -> list[str]:
    # Liste des bouts de phrases ou l'on doit refaire un scrapping pour trouver la bonne définition
    redos = ["pluriel de", "personne du", "du verbe"]

    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')

    # Tout les li contenant des définitions
    definitions = soup.find("ol").find_all("li")

    definition = definitions[0]
    definition_text = definition.getText()

    # Si une string de la liste redos est dans la définition
    if any(redo for redo in redos if redo in definition_text.lower()):
        parent_url = "https://fr.wiktionary.org" + definition.find("a")["href"]
        return scrapDefinition(parent_url)

    definition_split = definition_text.split("\n")

    return definition_split.pop(0), "\n".join(definition_split), url


def findDefinitions(word: str):
    url = f"https://fr.wiktionary.org/w/index.php?search={word}"
    try:
        return scrapDefinition(url)
    except:
        return None


difficulty_filters = {
    "easy": lambda x: (len(x) < 6),
    "medium": lambda x: (5 < len(x) < 9),
    "hard": lambda x: (8 < len(x))
}


def generateEmbed(phrase, word, avatar_url):
    definition = findDefinitions(word)

    url = ""

    if definition is not None:
        definition, example, url = definition

        fields = [
            interactions.EmbedField(
                name="Définition",
                value=definition,
                inline=False
            ),
            interactions.EmbedField(
                name="Exemple",
                value=example,
                inline=False
            )
        ]
    else:
        fields = [
            interactions.EmbedField(
                name="Définition",
                value="Franchement même le bot a pas trouvé la définition donc c'est pas grave si t'as pas trouvé."
            )
        ]

    thumbnail = None

    if avatar_url:
        thumbnail = interactions.EmbedImageStruct(url=avatar_url)

    embed = interactions.Embed(
        title=phrase,
        description=f"Tu as trouvé le mot [**{word}**]({url}) !",
        fields=fields,
        thumbnail=thumbnail
    )

    return embed
