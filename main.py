from telethon import TelegramClient, events, sync
from datetime import datetime, timedelta
import json

api_id = '12015405'  # Replace with your API ID
api_hash = '73807b76f1e21a0e193a9df14e9a3e41'  # Replace with your API hash
bot_token = '7304855416:AAHBDfvNK8LCFgGxwO172qn2EebJ-BQqnd4'  # Replace with your bot token

# Telethon client setup
client = TelegramClient('bot', api_id, api_hash).start(bot_token=bot_token)

# Path to the JSON file for storing user data
user_data_file = 'user_data.json'

# Path to the keys file
keys_file = 'keys.txt'

# Function to get user data
def get_user_data(user_id):
    try:
        with open(user_data_file, 'r') as f:
            content = f.read()
            if not content:  # Check if the file is empty
                return None
            user_data = json.loads(content)
        return user_data.get(str(user_id))
    except FileNotFoundError:
        return None
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {user_data_file}")
        return None
    
# Function to save user data
def save_user_data(user_id, activation_date):
    try:
        with open(user_data_file, 'r') as f:
            content = f.read()
            if not content:  # Check if the file is empty
                user_data = {}
            else:
                user_data = json.loads(content)
    except FileNotFoundError:
        user_data = {}
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {user_data_file}")
        user_data = {}

    user_data[str(user_id)] = activation_date.strftime('%Y-%m-%d')
    with open(user_data_file, 'w') as f:
        json.dump(user_data, f)

# Function to read keys from file
def read_keys():
    with open(keys_file, 'r') as f:
        return [line.strip() for line in f.readlines()]

# Function to remove a redeemed key from the file
def remove_key(redeemed_key):
    keys = read_keys()
    keys.remove(redeemed_key)
    with open(keys_file, 'w') as f:
        f.writelines('\n'.join(keys))

# Command handler for /start
@client.on(events.NewMessage(pattern='/start'))
async def start_handler(event):
    await event.respond('**🐣Welcome To The Predictūm Pro Leak Bot.**\n\nContact Admin For Queries')

# Command handler for /account
@client.on(events.NewMessage(pattern='/account'))
async def account_handler(event):
    user_data = get_user_data(event.sender_id)
    if user_data:
        activation_date = datetime.strptime(user_data, '%Y-%m-%d')
        days_left = (activation_date + timedelta(days=7) - datetime.now()).days
        if days_left > 0:
            await event.respond(f'**📈Account Information**:\n**👤Username:** {event.sender.username}\n⏳**Days Left:** {days_left}\n🚀**Plan Name:** Predictūm Pro Weekly')
        else:
            await event.respond('**❌Your plan has expired.**')
    else:
        await event.respond('**❌You do not have an active plan.**')

# Key redemption logic
@client.on(events.NewMessage(pattern='/redeem (.+)'))
async def redeem_handler(event):
    key_to_redeem = event.pattern_match.group(1).strip()
    keys = read_keys()
    if key_to_redeem in keys:
        save_user_data(event.sender_id, datetime.now())
        remove_key(key_to_redeem)  # Remove the redeemed key from the file
        await event.respond('**✅Key redeemed successfully! You now have access to Predictum Pro Weekly for 7 days.**')
    else:
        await event.respond('**❌The key you provided is invalid or has already been used.**')

# Function to check if a user's subscription is active
def is_subscription_active(user_data):
    activation_date = datetime.strptime(user_data, '%Y-%m-%d')
    return (activation_date + timedelta(days=7)) > datetime.now()

# Function to broadcast a message to active subscribers
async def broadcast_to_active_subscribers(message):
    try:
        with open(user_data_file, 'r') as f:
            user_data = json.load(f)
    except FileNotFoundError:
        print("No user data file found.")
        return

    for user_id, activation_date in user_data.items():
        if is_subscription_active(activation_date):
            try:
                await client.send_message(int(user_id), message)
            except Exception as e:
                print(f"Failed to send message to {user_id}: {e}")

# Command handler for /broadcast
@client.on(events.NewMessage(pattern='/broadcast (.+)'))
async def broadcast_handler(event):
    # Only allow the bot owner to broadcast messages
    if event.sender_id == 7207727106:  # Replace with your own user ID
        message_to_broadcast = event.pattern_match.group(1).strip()
        await broadcast_to_active_subscribers(message_to_broadcast)
        await event.respond('Message broadcasted to active subscribers.')
    else:
        await event.respond('You do not have permission to broadcast messages.')

# Start the bot
client.run_until_disconnected()