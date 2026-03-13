import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

# Replace these with your actual credentials or use environment variables
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8699325575:AAHotYf2PFRS9UVZLWfQPdZXWrcpWAiSaYw")

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

def is_group(message):
    return message.chat.type in ['group', 'supergroup']

def is_private(message):
    return message.chat.type == 'private'

# In-memory settings for Vercel (Note: This will reset on Vercel cold starts)
# Format: { chat_id: {"link": True, "story": True, "forward": True} }
# True means "deletion is ACTIVE" (users cannot send them).
group_settings = {}

def get_setting(chat_id, feature):
    if chat_id not in group_settings:
        return True # default to deleting everything
    return group_settings[chat_id].get(feature, True)

def set_setting(chat_id, feature, value):
    if chat_id not in group_settings:
        group_settings[chat_id] = {"link": True, "story": True, "forward": True}
    if feature == "all":
        group_settings[chat_id] = {"link": value, "story": value, "forward": value}
    else:
        group_settings[chat_id][feature] = value

def has_unwanted_content(message):
    chat_id = message.chat.id
    
    # Check for forwards
    if get_setting(chat_id, "forward"):
        if hasattr(message, 'forward_date') and message.forward_date is not None:
            return True
        if hasattr(message, 'json') and message.json and message.json.get('forward_origin'):
            return True
    
    # Check for story
    if get_setting(chat_id, "story"):
        if hasattr(message, "story") and message.story is not None:
            return True
        if hasattr(message, 'json') and message.json and message.json.get('story'):
            return True

    # Check for links in text and caption
    if get_setting(chat_id, "link"):
        entities = message.entities or []
        caption_entities = message.caption_entities or []
        all_entities = entities + caption_entities
        
        for entity in all_entities:
            if entity.type in ['url', 'text_link']:
                return True
                
    return False

def get_mentions(message):
    """Extracts all mentioned usernames from the message"""
    mentions = []
    entities = message.entities or []
    caption_entities = message.caption_entities or []
    all_entities = entities + caption_entities
    
    for entity in all_entities:
        if entity.type == 'mention':
            # Extract the mentioned username
            text_to_parse = message.text if message.text else message.caption
            if text_to_parse:
                mention = text_to_parse[entity.offset:entity.offset + entity.length]
                mentions.append(mention)
    return mentions

@bot.message_handler(commands=['start'], func=is_private)
def start_private(message):
    bot.reply_to(message, "ទាញអញចូល group gg ចាំអញលុប links story forward គេអោយតែដាក់អញ admin ផង☺️🖕")

@bot.message_handler(commands=['disablelink', 'disablestory', 'disableforward', 'enableall'], func=is_group)
def group_filters_setup(message):
    # Check admin
    try:
        chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
        if chat_member.status not in ['administrator', 'creator']:
            bot.reply_to(message, "Only admins can change these settings.")
            return
    except Exception:
        pass # Ignore failure to check (might not be admin)

    command = message.text.split()[0][1:].split('@')[0].lower()
    
    if command == 'disablelink':
        set_setting(message.chat.id, 'link', True)
        bot.reply_to(message, "✅ Links disabled (Bot will delete links).")
    elif command == 'disablestory':
        set_setting(message.chat.id, 'story', True)
        bot.reply_to(message, "✅ Stories disabled (Bot will delete stories).")
    elif command == 'disableforward':
        set_setting(message.chat.id, 'forward', True)
        bot.reply_to(message, "✅ Forwards disabled (Bot will delete forwards).")
    elif command == 'enableall':
        set_setting(message.chat.id, 'all', False)
        bot.reply_to(message, "✅ All features enabled (Users can send anything).")

@bot.message_handler(commands=['start', 'links', 'story', 'forward', 'filters'], func=is_group)
def group_commands(message):
    # Extract command part (e.g., '/start@botusername' -> 'start')
    command = message.text.split()[0][1:].split('@')[0]
    
    if command == 'start':
        bot.reply_to(message, "ទាញអញចូល group gg ចាំអញលុប links story forward គេអោយតែដាក់អញ admin ផង☺️🖕")
        return
        
    text = (
        "Active Commands in Group:\n"
        "✅ /links - Delete links status\n"
        "✅ /story - Delete stories status\n"
        "✅ /forward - Delete forwards status\n"
        "✅ /filters - Show this menu"
    )
    bot.reply_to(message, text)

@bot.message_handler(content_types=['new_chat_members'])
def welcome_new_bot(message):
    me = bot.get_me()
    for member in message.new_chat_members:
        if member.id == me.id:
            markup = InlineKeyboardMarkup()
            button = InlineKeyboardButton(
                "Promote to Admin 👮‍♂️", 
                url=f"https://t.me/{me.username}?startgroup=true&admin=delete_messages+restrict_members"
            )
            markup.add(button)
            
            bot.send_message(
                message.chat.id,
                "សួស្តី! អរគុណដែលបានទាញខ្ញុំចូល group។\n"
                "សូមកុំភ្លេច Promote ខ្ញុំជា Admin ដើម្បីអោយខ្ញុំអាចលុប links, story, និង forward បាន!",
                reply_markup=markup
            )
            break

# Handler for all messages in groups to check for links/forwards/stories AND MENTIONS
@bot.message_handler(func=is_group, content_types=['text', 'photo', 'video', 'document', 'audio', 'voice', 'animation', 'sticker', 'story', 'location'])
def check_messages(message):
    # 1. Check for unwanted content (links, forwards, stories)
    if has_unwanted_content(message):
        # Check if user is an administrator
        if message.from_user:
            try:
                chat_member = bot.get_chat_member(message.chat.id, message.from_user.id)
                if chat_member.status in ['administrator', 'creator']:
                    return  # User is admin, do not delete their messages
            except Exception as e:
                pass # Safe check gracefully skipped
                
        try:
            bot.delete_message(message.chat.id, message.message_id)
            if message.from_user:
                username = f"@{message.from_user.username}" if message.from_user.username else message.from_user.first_name
                reply_text = f"{username}អត់ការងារធ្វើមែនបានចេះតែ share ចូល group គេហ្នឹង។☺️🖕"
                reply = bot.send_message(message.chat.id, reply_text)
                return # Stop processing this message since it was deleted
                
        except Exception as e:
            print(f"Could not delete message in group: {e}")
            
    # 2. Check for mentions (if the message wasn't deleted above)
    mentions = get_mentions(message)
    if mentions:
        for username in mentions:
            # Send an alert notification tag
            alert_text = f"🔔 {username} You have been mentioned in this chat by {message.from_user.first_name}!"
            try:
                bot.send_message(message.chat.id, alert_text, reply_to_message_id=message.message_id)
            except Exception as e:
                print(f"Could not send mention alert: {e}")

if __name__ == "__main__":
    try:
        me = bot.get_me()
        print("Group Guardian Bot is running locally (pyTelegramBotAPI)...")
        print("To auto-prompt users to add this bot as an admin, give them this link:")
        print(f"https://t.me/{me.username}?startgroup=true&admin=delete_messages+restrict_members")
        # Start polling (only runs when executed directly, not when imported by Vercel)
        bot.remove_webhook()
        bot.infinity_polling()
    except Exception as e:
        print(f"Failed to start bot: {e}")
