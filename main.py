import requests
from typing import Any


class PokeAPIClient:
    def __init__(self, base_url: str):
        self.base_url = base_url

    def get_pokemon_list(self, limit: int = 100, offset: int = 0) -> dict[Any, Any]:
        """Get a list of Pokémon with optional pagination."""
        endpoint = f'/pokemon?limit={limit}&offset={offset}'
        response = requests.get(self.base_url + endpoint)
        return response.json()

    def get_pokemon_by_id(self, pokemon_id: int) -> dict[Any, Any]:
        """Get details of a Pokémon by its ID."""
        endpoint = f'/pokemon/{pokemon_id}'
        response = requests.get(self.base_url + endpoint)
        return response.json()

    def get_pokemon_image_url(self, pokemon_name: str) -> str:
        """Retrieve the URL of a Pokémon's image by its name."""
        endpoint = f'/pokemon/{pokemon_name}'
        response = requests.get(self.base_url + endpoint)
        if response.status_code == 200:
            pokemon_data = response.json()
            return pokemon_data['sprites']['front_default']
        return "Image not available"



from telebot import TeleBot
from telebot.types import Message



TOKEN = ''


class PokemonBot(TeleBot):
    def __init__(self, pokemon_api_client: PokeAPIClient,
                 token: str, *args, **kwargs):
        super().__init__(token=token, *args, **kwargs)
        self.pokemon_api_client = pokemon_api_client


pokemon_api_client = PokeAPIClient(base_url="https://pokeapi.co/api/v2")

bot = PokemonBot(token=TOKEN, pokemon_api_client=pokemon_api_client)


@bot.message_handler(commands=['start'])
def start(message: Message):
    bot.reply_to(message, text="Welcome to the Pokemon bot")


@bot.message_handler(commands=['get_pokemons'])
def get_pokemon_list(message: Message):
    pokemons = bot.pokemon_api_client.get_pokemon_list(limit=10)
    result = "\n".join([f' {pokemon_data["name"]}' for pokemon_data in pokemons["results"]])
    bot.send_message(chat_id=message.chat.id, text=result)


@bot.message_handler(commands=['get_pokemon_image'])
def get_pokemon_image(message: Message):
    try:
        pokemon_name = message.text.split()[
            1]  # предполагается, что команда идет в формате '/get_pokemon_image pikachu'
    except IndexError:
        bot.reply_to(message, "Please provide a Pokémon name.")
        return

    image_url = bot.pokemon_api_client.get_pokemon_image_url(pokemon_name)
    if image_url != "Image not available":
        bot.send_photo(chat_id=message.chat.id, photo=image_url)
    else:
        bot.send_message(chat_id=message.chat.id, text="Failed to retrieve Pokémon image.")


@bot.message_handler(commands=['location'])
def send_location(message: Message):
    chat_id = message.chat.id
    bot.send_location(chat_id, 69.30, 65)


bot.polling()
