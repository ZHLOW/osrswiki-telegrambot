import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

TOKEN = os.getenv('TOKEN')
ITEM_PRICES_URL = "https://prices.runescape.wiki/api/v1/osrs/latest"
ITEM_MAPPING_URL = "https://prices.runescape.wiki/api/v1/osrs/mapping"
ITEM_DETAIL_URL = "https://secure.runescape.com/m=itemdb_oldschool/api/catalogue/detail.json?item={}"

# Fetch item ID mapping at startup
response = requests.get(ITEM_MAPPING_URL)
item_data = response.json() if response.status_code == 200 else []
ITEM_MAPPING = {item["name"].lower(): item for item in item_data} if isinstance(item_data, list) else {}

async def start(update: Update, context: CallbackContext):
    """Welcome message."""
    message = (
        "👋 Welcome to OSRS Saudi Bot!\n"
        "Use the commands:\n"
        "/start - Welcome message\n"
        "/item <name> - Get item prices & image\n"
        "/stats <username> - Get player stats\n"
        "/mob <name> - Get monster stats\n"
        "/wiki <query> - Search OSRS Wiki\n"
        "/house - Joel's house progress\n"
    )
    await update.message.reply_text(message)

async def item(update: Update, context: CallbackContext):
    """Fetch item price, large icon & wiki link."""
    
    if not context.args:
        await update.message.reply_text("Usage: /item <item_name>")
        return
    
    item_name = " ".join(context.args).lower()
    item = ITEM_MAPPING.get(item_name)
    
    if not item:
        await update.message.reply_text("⚠️ Item not found. Check spelling.")
        return

    # Fetching the price data
    response = requests.get(ITEM_PRICES_URL)
    data = response.json().get("data", {})
    item_id = str(item["id"])
    price_data = data.get(item_id, {})

    # Fetching the large icon for the item
    item_detail_response = requests.get(ITEM_DETAIL_URL.format(item["id"]))
    item_detail_data = item_detail_response.json()
    icon_large = item_detail_data.get("item", {}).get("icon_large", "")

    # Prepare the price information
    price_text = (
        f"💰 **{item['name']}**\n"
        f"- 📈 High: {price_data.get('high', 0):,} gp\n"
        f"- 📉 Low: {price_data.get('low', 0):,} gp\n"
        f"- 🔗 [Item Wiki Link](https://oldschool.runescape.wiki/w/{item_name.replace(' ', '_')})"
    )
    
    # Sending the message with large icon and price details
    await update.message.reply_photo(photo=icon_large, caption=price_text, parse_mode="Markdown")

async def stats(update: Update, context: CallbackContext) -> None:
    if not context.args:
        await update.message.reply_text("Please provide a username. Usage: /stats <username>")
        return
    
    username = context.args[0]
    hiscores_url = f"https://secure.runescape.com/m=hiscore_oldschool/index_lite.json?player={username}"
    
    response = requests.get(hiscores_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()

        # List of skills
        skills = [
            ("Total Level", data['skills'][0]['level']),

            ("⚔️ Attack", data['skills'][1]['level']),
            ("💪 Strength", data['skills'][3]['level']),
            ("🛡️ Defense", data['skills'][2]['level']),
            ("🏹 Ranged", data['skills'][5]['level']),
            ("✨ Prayer", data['skills'][6]['level']),
            ("🧙‍♂️ Magic", data['skills'][7]['level']),
            ("❤️ Hitpoints", data['skills'][4]['level']),

            ("🏃 Agility", data['skills'][17]['level']),
            ("🍀 Herblore", data['skills'][16]['level']),
            ("🕶️ Thieving", data['skills'][18]['level']),
            ("🛠️ Crafting", data['skills'][13]['level']),
            ("🥢 Fletching", data['skills'][10]['level']),
            ("⛏️ Mining", data['skills'][15]['level']),
            ("🔨 Smithing", data['skills'][14]['level']),
            ("🎣 Fishing", data['skills'][11]['level']),
            ("🥧 Cooking", data['skills'][8]['level']),
            ("🔥 Firemaking", data['skills'][12]['level']),
            ("🌳 Woodcutting", data['skills'][9]['level']),
            ("⚡ Runecrafting", data['skills'][21]['level']),
            ("💀 Slayer", data['skills'][19]['level']),
            ("👩🏻‍🌾 Farming", data['skills'][20]['level']),
            ("🏠 Construction", data['skills'][23]['level']),
            ("🐾 Hunter", data['skills'][22]['level']),
        ]
        
        # Example: Accessing the "skills" data
        message = ""
        message += f"Displaying Stats for --- {username}\n\nTotal Level: {skills[0][1]}\n\n"

        for i in range(1, len(skills)):
            message += f"{str(skills[i][0])}: {str(skills[i][1])}\n"
            if i == 7:
                message += "\n"
              
        await update.message.reply_text(message)
        
    else:
        await update.message.reply_text(f"{username} is a bot 🤖")

async def mob(update: Update, context: CallbackContext):
    """Fetch OSRS monster stats."""
    if not context.args:
        await update.message.reply_text("Usage: /mob <monster_name>")
        return

    mob_name = "_".join(context.args)
    wiki_url = f"https://oldschool.runescape.wiki/w/{mob_name}"
    await update.message.reply_text(f"🦴 **Monster Stats:**\n🔗 [Click here]({wiki_url})", parse_mode="Markdown")

async def wiki(update: Update, context: CallbackContext):
    """Returns an OSRS Wiki search link."""
    if not context.args:
        await update.message.reply_text("Usage: /wiki <query>")
        return
    
    # if response.status_code == 200 and response.status_code != 404:
    query = "_".join(context.args)
    wiki_url = f"https://oldschool.runescape.wiki/w/{query}"
    await update.message.reply_text(f"🔗 **OSRS Wiki:** [Click here]({wiki_url})", parse_mode="Markdown")
    
    # else:
    #     return f"Error fetching data."

async def house(update: Update, context: CallbackContext):
    """Returns Joel's house progress."""    
    hiscores_url = "https://secure.runescape.com/m=hiscore_oldschool/index_lite.json?player=Tricstar"
    response = requests.get(hiscores_url)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Parse the JSON data
        data = response.json()

        # List of skills
        skills = ("Construction", data['skills'][23]['level'], data['skills'][23]['xp'])

        # Example: Accessing the "skills" data
        message = f"🏠 Joel is {83-skills[1]} levels away from 83 Construction!\n\n🧰 Remaining XP: {2673114 - skills[2]:,}"

        await update.message.reply_text(message)

    else:
        return f"Error fetching stats."

def main():
    """Start the bot."""
    print("Bot is running...")
    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("item", item))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("mob", mob))
    application.add_handler(CommandHandler("wiki", wiki))
    application.add_handler(CommandHandler("house", house))
    
    application.run_polling()

if __name__ == "__main__":
    main()
