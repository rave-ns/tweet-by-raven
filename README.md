# Twitter Telegram Bot

A Telegram bot that allows users to interact with Twitter directly from Telegram. Post tweets, read profiles, and search for content without leaving Telegram.

## Features

* 🐦 **Post Tweets**: Create and publish tweets directly from Telegram
* 📖 **Read Tweets**: View the latest tweets from any public Twitter profile
* 🔍 **Search Twitter**: Find tweets that match specific keywords
* ⚙️ **Account Management**: Securely connect your Twitter account through API credentials
* 🔐 **Secure Storage**: All API keys are stored securely in MongoDB

## Screenshots

*(Insert screenshots of your bot in action)*

## Requirements

* Python 3.7+
* MongoDB database
* Twitter Developer Account with API credentials
* Telegram Bot Token

## Installation

1. Clone this repository:

```bash
git clone https://github.com/yourusername/twitter-telegram-bot.git
cd twitter-telegram-bot
```

2. Install the required packages:

```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project directory with the following variables:

```
TOKEN=your_telegram_bot_token
MONGO_URI=your_mongodb_connection_string
```

## Setup Instructions

### Creating a Telegram Bot

1. Talk to @BotFather on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the API token provided and add it to your `.env` file

### Setting Up Twitter API Access

1. Create a [Twitter Developer Account](https://developer.twitter.com/en/apply-for-access)
2. Create a new Project and App
3. Generate the required API credentials:
   * API Key
   * API Secret Key
   * Access Token
   * Access Token Secret

### Setting Up MongoDB

1. Create a [MongoDB Atlas account](https://www.mongodb.com/cloud/atlas/register) or use a self-hosted MongoDB instance
2. Create a new cluster and database named `users`
3. Create a collection named `keys`
4. Copy your MongoDB connection string and add it to your `.env` file

## Usage

Run the bot:

```bash
python bot.py
```

When users interact with your bot, they will need to:

1. Start the bot with `/start`
2. Navigate to Settings
3. Enter their Twitter API credentials
4. Test their connection
5. Start using Twitter features directly from Telegram

## Deployment

### Deploying to a VPS

1. Set up a server with Python installed
2. Clone this repository to your server
3. Install dependencies and set up your `.env` file
4. Use a process manager like `supervisor` or `systemd` to keep the bot running

Example `systemd` service file:
```ini
[Unit]
Description=Twitter Telegram Bot
After=network.target

[Service]
User=yourusername
WorkingDirectory=/path/to/twitter-telegram-bot
ExecStart=/usr/bin/python3 /path/to/twitter-telegram-bot/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```


2. Set up environment variables in Heroku dashboard
3. Deploy using Heroku CLI or GitHub integration

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Developed by [@Asqlan](https://t.me/Asqlan) on Telegram

## Acknowledgments

* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Makes creating Telegram bots easy
* [Tweepy](https://www.tweepy.org/) - Python library for accessing the Twitter API
