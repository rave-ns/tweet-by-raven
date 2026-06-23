from telebot import types, TeleBot
from dotenv import load_dotenv
from pymongo import MongoClient
import json
import os
import urllib.error
import urllib.request
import tweepy

load_dotenv()

XQUIK_API_BASE_URL = os.getenv('XQUIK_API_BASE_URL', 'https://xquik.com/api/v1').rstrip('/')

try:
    mongo = MongoClient(os.getenv('MONGO'))
    db = mongo['users']
    keys = db['keys']
except Exception as e:
    print(f"Error MongoClient", e)

bot = TeleBot(os.getenv('TOKEN'), parse_mode='HTML')
user_state = {}


def join_my_channel():
    markup = types.InlineKeyboardMarkup()
    join = types.InlineKeyboardButton(text='Join Our Channel', url='https://t.me/fctn5')
    markup.add(join)
    return markup


def account_setting():
    markup = types.InlineKeyboardMarkup(row_width=2)

    api_key = types.InlineKeyboardButton(text="API Key", callback_data='api_key')
    api_secret = types.InlineKeyboardButton(text='API Secret', callback_data='api_secret')
    tw_token = types.InlineKeyboardButton(text='Access Token', callback_data='token')
    token_secret = types.InlineKeyboardButton(text='Token Secret', callback_data='token_secret')
    xquik_api_key = types.InlineKeyboardButton(text='Xquik API Key', callback_data='xquik_api_key')
    xquik_account = types.InlineKeyboardButton(text='Xquik Account', callback_data='xquik_account')
    test_connection = types.InlineKeyboardButton(text='🔄 Test Connection', callback_data='test_connection')
    back = types.InlineKeyboardButton(text='⬅️ Back', callback_data='main_menu')

    markup.add(api_key, api_secret, tw_token, token_secret)
    markup.add(xquik_api_key, xquik_account)
    markup.add(test_connection)
    markup.add(back)
    return markup


def main_menu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    
    tweet = types.InlineKeyboardButton(text="✍️ Tweet", callback_data='tweet')
    read = types.InlineKeyboardButton(text="📖 Read Tweets", callback_data='read')
    search = types.InlineKeyboardButton(text="🔍 Search", callback_data='search')
    settings = types.InlineKeyboardButton(text="⚙️ Settings", callback_data='settings')
    
    markup.add(tweet, read)
    markup.add(search, settings)
    return markup


def back_to_settings():
    markup = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton(text="⬅️ Back to Settings", callback_data='settings')
    markup.add(back)
    return markup


def back_to_main():
    markup = types.InlineKeyboardMarkup()
    back = types.InlineKeyboardButton(text="⬅️ Back to Menu", callback_data='main_menu')
    markup.add(back)
    return markup


def cancel_markup():
    markup = types.InlineKeyboardMarkup()
    cancel = types.InlineKeyboardButton(text="❌ Cancel", callback_data='cancel_input')
    markup.add(cancel)
    return markup


def get_twitter_client(chat_id):
    user_keys = keys.find_one({'_id': chat_id})
    if not user_keys or 'api_key' not in user_keys or 'api_secret' not in user_keys or 'access_token' not in user_keys or 'access_token_secret' not in user_keys:
        return None
    
    try:
        auth = tweepy.OAuth1UserHandler(
            user_keys['api_key'], 
            user_keys['api_secret'],
            user_keys['access_token'], 
            user_keys['access_token_secret']
        )
        return tweepy.API(auth)
    except Exception as e:
        print(f"Error creating Twitter client: {e}")
        return None


def get_xquik_config(chat_id):
    user_keys = keys.find_one({'_id': chat_id})
    if not user_keys:
        return None

    api_key = user_keys.get('xquik_api_key')
    account = user_keys.get('xquik_account')
    if not api_key or not account:
        return None

    return {
        'api_key': api_key,
        'account': account,
        'base_url': user_keys.get('xquik_api_base_url') or XQUIK_API_BASE_URL,
    }


def post_tweet_with_xquik(tweet_text, config):
    payload = json.dumps({
        'account': config['account'],
        'text': tweet_text,
    }).encode('utf-8')
    request = urllib.request.Request(
        f"{config['base_url']}/x/tweets",
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'x-api-key': config['api_key'],
        },
        method='POST',
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            body = response.read().decode('utf-8')
            if response.status not in (200, 202):
                raise RuntimeError(f"Xquik post failed with status {response.status}: {body[:300]}")
            return json.loads(body)
    except urllib.error.HTTPError as error:
        body = error.read().decode('utf-8', errors='replace')
        raise RuntimeError(f"Xquik post failed with status {error.code}: {body[:300]}") from error


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    message_id = message.message_id
    bot.send_message(
        chat_id,
        text=(
            "🐦 <b>Welcome to Twitter Bot!</b>\n\n"
            "I'm here to help you interact with Twitter directly from Telegram.\n\n"
            "Use the buttons below to navigate through my features:"
        ),
        reply_markup=main_menu(),
        reply_to_message_id=message_id
    )


@bot.callback_query_handler(func=lambda call: True)
def call_handler(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    
    if call.data == 'main_menu':
        bot.edit_message_text(
            text="🐦 <b>Twitter Bot Main Menu</b>\n\nSelect an option below:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=main_menu()
        )
        
    elif call.data == 'settings':
        bot.edit_message_text(
            text="⚙️ <b>Account Settings</b>\n\n"
                 "Set Twitter credentials for read/search features, or Xquik credentials for posting.\n\n"
                 "Click each button to configure the account:",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=account_setting()
        )
        
    elif call.data == 'api_key':
        user_state[chat_id] = 'awaiting_api_key'
        bot.edit_message_text(
            text="🔑 <b>Enter your Twitter API Key</b>\n\n"
                 "Please reply to this message with your API Key.\n\n"
                 "<i>You can find this in the Twitter Developer Portal under Keys and Tokens.</i>",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=cancel_markup()
        )
        
    elif call.data == 'api_secret':
        user_state[chat_id] = 'awaiting_api_secret'
        bot.edit_message_text(
            text="🔑 <b>Enter your Twitter API Secret</b>\n\n"
                 "Please reply to this message with your API Secret.\n\n"
                 "<i>You can find this in the Twitter Developer Portal under Keys and Tokens.</i>",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=cancel_markup()
        )
        
    elif call.data == 'token':
        user_state[chat_id] = 'awaiting_token'
        bot.edit_message_text(
            text="🔑 <b>Enter your Twitter Access Token</b>\n\n"
                 "Please reply to this message with your Access Token.\n\n"
                 "<i>You can find this in the Twitter Developer Portal under Keys and Tokens.</i>",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=cancel_markup()
        )
        
    elif call.data == 'token_secret':
        user_state[chat_id] = 'awaiting_token_secret'
        bot.edit_message_text(
            text="🔑 <b>Enter your Twitter Access Token Secret</b>\n\n"
                 "Please reply to this message with your Access Token Secret.\n\n"
                 "<i>You can find this in the Twitter Developer Portal under Keys and Tokens.</i>",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=cancel_markup()
        )

    elif call.data == 'xquik_api_key':
        user_state[chat_id] = 'awaiting_xquik_api_key'
        bot.edit_message_text(
            text="🔑 <b>Enter your Xquik API Key</b>\n\n"
                 "This is used only for posting tweets through Xquik.",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=cancel_markup()
        )

    elif call.data == 'xquik_account':
        user_state[chat_id] = 'awaiting_xquik_account'
        bot.edit_message_text(
            text="👤 <b>Enter your Xquik Account</b>\n\n"
                 "Use the connected X account handle, such as @your_handle.",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=cancel_markup()
        )
        
    elif call.data == 'cancel_input':
        if chat_id in user_state:
            del user_state[chat_id]
        bot.edit_message_text(
            text="❌ Input cancelled. What would you like to do?",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=account_setting()
        )
        
    elif call.data == 'test_connection':
        client = get_twitter_client(chat_id)
        if not client:
            bot.edit_message_text(
                text="❌ <b>Connection Failed</b>\n\n"
                     "Twitter connection could not be established. Please check your API credentials "
                     "and ensure all four keys are properly set up.",
                chat_id=chat_id,
                message_id=message_id,
                reply_markup=account_setting()
            )
        else:
            try:
                user = client.verify_credentials()
                bot.edit_message_text(
                    text=f"✅ <b>Connection Successful!</b>\n\n"
                         f"Connected to Twitter as: <b>@{user.screen_name}</b>\n"
                         f"Name: {user.name}\n"
                         f"Followers: {user.followers_count}\n"
                         f"Following: {user.friends_count}\n\n"
                         f"You're all set to use the Twitter bot!",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=account_setting()
                )
            except Exception as e:
                bot.edit_message_text(
                    text=f"❌ <b>Connection Error</b>\n\n"
                         f"Error verifying credentials: {str(e)}\n\n"
                         f"Please check your API keys and try again.",
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=account_setting()
                )
                
    elif call.data == 'tweet':
        user_state[chat_id] = 'awaiting_tweet'
        bot.edit_message_text(
            text="✍️ <b>Create a Tweet</b>\n\n"
                 "Please reply to this message with the content for your tweet.\n\n"
                 "<i>Remember: Tweets are limited to 280 characters.</i>",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=cancel_markup()
        )
        
    elif call.data == 'read':
        user_state[chat_id] = 'awaiting_read_username'
        bot.edit_message_text(
            text="📖 <b>Read Tweets</b>\n\n"
                 "Please reply to this message with the Twitter username you want to read tweets from.\n\n"
                 "<i>Don't include the @ symbol - just enter the username.</i>",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=cancel_markup()
        )
        
    elif call.data == 'search':
        user_state[chat_id] = 'awaiting_search_query'
        bot.edit_message_text(
            text="🔍 <b>Search Tweets</b>\n\n"
                 "Please reply to this message with the keywords you want to search for on Twitter.",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=cancel_markup()
        )


@bot.message_handler(func=lambda message: True)
def handle_messages(message):
    chat_id = message.chat.id
    
    if chat_id not in user_state:
        bot.send_message(
            chat_id,
            "Please use the main menu to access features:",
            reply_markup=main_menu()
        )
        return
        
    current_state = user_state[chat_id]
    
    if current_state == 'awaiting_api_key':
        api_key = message.text.strip()
        keys.update_one({'_id': chat_id}, {'$set': {'api_key': api_key}}, upsert=True)
        del user_state[chat_id]
        bot.send_message(
            chat_id,
            "✅ <b>API Key saved successfully!</b>\n\nWhat would you like to configure next?",
            reply_markup=account_setting()
        )
        
    elif current_state == 'awaiting_api_secret':
        api_secret = message.text.strip()
        keys.update_one({'_id': chat_id}, {'$set': {'api_secret': api_secret}}, upsert=True)
        del user_state[chat_id]
        bot.send_message(
            chat_id,
            "✅ <b>API Secret saved successfully!</b>\n\nWhat would you like to configure next?",
            reply_markup=account_setting()
        )
        
    elif current_state == 'awaiting_token':
        access_token = message.text.strip()
        keys.update_one({'_id': chat_id}, {'$set': {'access_token': access_token}}, upsert=True)
        del user_state[chat_id]
        bot.send_message(
            chat_id,
            "✅ <b>Access Token saved successfully!</b>\n\nWhat would you like to configure next?",
            reply_markup=account_setting()
        )
        
    elif current_state == 'awaiting_token_secret':
        token_secret = message.text.strip()
        keys.update_one({'_id': chat_id}, {'$set': {'access_token_secret': token_secret}}, upsert=True)
        del user_state[chat_id]
        bot.send_message(
            chat_id,
            "✅ <b>Access Token Secret saved successfully!</b>\n\nAll credentials are now saved. Would you like to test your connection?",
            reply_markup=account_setting()
        )

    elif current_state == 'awaiting_xquik_api_key':
        xquik_api_key = message.text.strip()
        keys.update_one({'_id': chat_id}, {'$set': {'xquik_api_key': xquik_api_key}}, upsert=True)
        del user_state[chat_id]
        bot.send_message(
            chat_id,
            "✅ <b>Xquik API Key saved successfully!</b>\n\nAdd the Xquik account handle next.",
            reply_markup=account_setting()
        )

    elif current_state == 'awaiting_xquik_account':
        xquik_account = message.text.strip()
        keys.update_one({'_id': chat_id}, {'$set': {'xquik_account': xquik_account}}, upsert=True)
        del user_state[chat_id]
        bot.send_message(
            chat_id,
            "✅ <b>Xquik Account saved successfully!</b>\n\nPosting will use Xquik when both Xquik fields are set.",
            reply_markup=account_setting()
        )
        
    elif current_state == 'awaiting_tweet':
        tweet_text = message.text.strip()
        del user_state[chat_id]

        if len(tweet_text) > 280:
            bot.send_message(
                chat_id,
                f"❌ Your tweet is {len(tweet_text)} characters long. Twitter has a limit of 280 characters.",
                reply_markup=main_menu()
            )
            return

        xquik_config = get_xquik_config(chat_id)
        if xquik_config:
            try:
                result = post_tweet_with_xquik(tweet_text, xquik_config)
                tweet_id = result.get('tweetId')
                if tweet_id:
                    bot.send_message(
                        chat_id,
                        f"✅ <b>Tweet posted successfully with Xquik!</b>\n\n"
                        f"🔗 <a href='https://x.com/i/status/{tweet_id}'>View your tweet</a>",
                        reply_markup=main_menu()
                    )
                    return

                write_action_id = result.get('writeActionId', 'pending')
                bot.send_message(
                    chat_id,
                    f"✅ <b>Tweet accepted by Xquik.</b>\n\n"
                    f"Confirmation is pending. Write action: <code>{write_action_id}</code>",
                    reply_markup=main_menu()
                )
                return
            except Exception as e:
                bot.send_message(
                    chat_id,
                    f"❌ Error posting tweet with Xquik: {str(e)}",
                    reply_markup=main_menu()
                )
                return
        
        client = get_twitter_client(chat_id)
        if not client:
            bot.send_message(
                chat_id,
                "❌ Twitter connection not established. Please configure your API keys first.",
                reply_markup=account_setting()
            )
            return
            
        try:
            tweet = client.update_status(tweet_text)
            username = tweet.user.screen_name
            tweet_id = tweet.id
            bot.send_message(
                chat_id,
                f"✅ <b>Tweet posted successfully!</b>\n\n"
                f"🔗 <a href='https://twitter.com/{username}/status/{tweet_id}'>View your tweet</a>",
                reply_markup=main_menu()
            )
        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Error posting tweet: {str(e)}",
                reply_markup=main_menu()
            )
            
    elif current_state == 'awaiting_read_username':
        username = message.text.strip().replace('@', '')
        del user_state[chat_id]
        
        client = get_twitter_client(chat_id)
        if not client:
            bot.send_message(
                chat_id,
                "❌ Twitter connection not established. Please configure your API keys first.",
                reply_markup=account_setting()
            )
            return
            
        try:
            tweets = client.user_timeline(screen_name=username, count=5, tweet_mode='extended')
            
            if not tweets:
                bot.send_message(
                    chat_id,
                    f"No tweets found from @{username} or this account may be private.",
                    reply_markup=main_menu()
                )
                return
                
            response = f"📱 <b>Latest tweets from @{username}</b>\n\n"
            
            for tweet in tweets:
                tweet_text = tweet.full_text
                tweet_date = tweet.created_at.strftime("%Y-%m-%d %H:%M")
                tweet_url = f"https://twitter.com/{username}/status/{tweet.id}"
                response += f"🕒 <i>{tweet_date}</i>\n{tweet_text}\n🔗 <a href='{tweet_url}'>View tweet</a>\n\n"
                
            bot.send_message(
                chat_id, 
                response,
                reply_markup=main_menu()
            )
        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Error reading tweets: {str(e)}",
                reply_markup=main_menu()
            )
            
    elif current_state == 'awaiting_search_query':
        query = message.text.strip()
        del user_state[chat_id]
        
        client = get_twitter_client(chat_id)
        if not client:
            bot.send_message(
                chat_id,
                "❌ Twitter connection not established. Please configure your API keys first.",
                reply_markup=account_setting()
            )
            return
            
        try:
            tweets = client.search_tweets(q=query, count=5, tweet_mode='extended')
            
            if not tweets or len(list(tweets)) == 0:
                bot.send_message(
                    chat_id,
                    f"No tweets found matching '{query}'.",
                    reply_markup=main_menu()
                )
                return
                
            response = f"🔎 <b>Search results for '{query}'</b>\n\n"
            
            for tweet in tweets:
                author = tweet.user.screen_name
                tweet_text = tweet.full_text
                tweet_date = tweet.created_at.strftime("%Y-%m-%d %H:%M")
                tweet_url = f"https://twitter.com/{author}/status/{tweet.id}"
                response += f"👤 <b>@{author}</b> - <i>{tweet_date}</i>\n{tweet_text}\n🔗 <a href='{tweet_url}'>View tweet</a>\n\n"
                
            bot.send_message(
                chat_id,
                response,
                reply_markup=main_menu()
            )
        except Exception as e:
            bot.send_message(
                chat_id,
                f"❌ Error searching tweets: {str(e)}",
                reply_markup=main_menu()
            )


if __name__ == '__main__':
    bot.polling(timeout=30)
