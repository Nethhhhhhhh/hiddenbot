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

def has_unwanted_content(message):
    # Check for forwards
    if hasattr(message, 'forward_date') and message.forward_date is not None:
        return True
    if hasattr(message, 'json') and message.json and message.json.get('forward_origin'):
        return True
    
    # Check for story (Telebot might not fully support this natively yet, but we check if attribute exists)
    if hasattr(message, "story") and message.story is not None:
        return True
    if hasattr(message, 'json') and message.json and message.json.get('story'):
        return True

    # Check for links in text and caption
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
