from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
import os

# Replace these with your actual credentials or use environment variables
API_ID = os.environ.get("API_ID", 32547622)
API_HASH = os.environ.get("API_HASH", "f00c0be12c0278e4d1211d062f4e4804")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8699325575:AAHotYf2PFRS9UVZLWfQPdZXWrcpWAiSaYw")

# Make sure the session file is saved exactly where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))
app = Client("mikita", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN, workdir=script_dir)

# Custom filter for stories since filters.story might not be available
is_story = filters.create(lambda _, __, message: bool(getattr(message, "story", None)))

def check_has_link(_, __, message: Message):
    entities = message.entities or message.caption_entities or []
    for entity in entities:
        # Check both Pyrogram 1.x (str) and 2.x (Enum)
        type_str = getattr(entity.type, "name", str(entity.type)).upper()
        if type_str in ["URL", "TEXT_LINK", "MESSAGEENTITYTYPE.URL", "MESSAGEENTITYTYPE.TEXT_LINK"]:
            return True
    return False

has_link = filters.create(check_has_link)

# Filter for links, forwards (shares), and stories
unwanted_filters = filters.group & (
    filters.forwarded | 
    is_story | 
    has_link
)

@app.on_message(filters.command("start") & filters.private)
async def start_command(client: Client, message: Message):
    await message.reply_text("ទាញអញចូល group gg ចាំអញលុប links story forward គេអោយតែដាក់អញ admin ផង☺️🖕")

@app.on_message(filters.command(["start", "links", "story", "forward", "filters"]) & filters.group)
async def group_commands_handler(client: Client, message: Message):
    if message.command[0] == "start":
        await message.reply_text("ទាញអញចូល group gg ចាំអញលុប links story forward គេអោយតែដាក់អញ admin ផង☺️🖕")
        return
        
    text = (
        "Active Commands in Group:\n"
        "✅ /links - Delete links status\n"
        "✅ /story - Delete stories status\n"
        "✅ /forward - Delete forwards status\n"
        "✅ /filters - Show this menu"
    )
    await message.reply_text(text)

@app.on_message(unwanted_filters)
async def delete_unwanted_messages(client: Client, message: Message):
    # Optionally, we can check if the user is an administrator and skip deleting their messages
    if message.from_user:
        chat_member = await client.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.privileges:
            # User has admin privileges, do not delete their messages
            return
            
    try:
        await message.delete()
        if message.from_user:
            username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
            reply_text = f"{username}អត់ការងារធ្វើមែនបានចេះតែ share ចូល group គេហ្នឹង។☺️🖕"
            await client.send_message(message.chat.id, reply_text)
    except Exception as e:
        print(f"Could not delete message in {message.chat.id}: {e}")

@app.on_message(filters.new_chat_members)
async def welcome_bot(client: Client, message: Message):
    for member in message.new_chat_members:
        if member.is_self:
            # Bot was added to a group. Find out its username using get_me
            me = await client.get_me()
            button = InlineKeyboardMarkup([
                [InlineKeyboardButton("Promote to Admin 👮‍♂️", url=f"https://t.me/{me.username}?startgroup=true&admin=delete_messages+restrict_members")]
            ])
            await message.reply_text(
                "សួស្តី! អរគុណដែលបានទាញខ្ញុំចូល group។\n"
                "សូមកុំភ្លេច Promote ខ្ញុំជា Admin ដើម្បីអោយខ្ញុំអាចលុប links, story, និង forward បាន!",
                reply_markup=button
            )
            break

if __name__ == "__main__":
    print("Group Guardian Bot is running...")
    print("To auto-prompt users to add this bot as an admin, give them this link:")
    print("https://t.me/hiddenmikitabot?startgroup=true&admin=delete_messages+restrict_members")
    app.run()
