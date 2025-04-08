# Twitter Telegram Bot 🐦💬

A Telegram bot that allows users to interact with Twitter directly from Telegram. Post tweets, read profiles, and search for content without leaving Telegram.

## Features

* 🐦 **Post Tweets**: Create and publish tweets directly from Telegram
* 📖 **Read Tweets**: View the latest tweets from any public Twitter profile
* 🔍 **Search Twitter**: Find tweets that match specific keywords
* ⚙️ **Account Management**: Securely connect your Twitter account through API credentials
* 🔐 **Secure Storage**: All API keys are stored securely in MongoDB

## ⚠️ Important Note About Twitter API

Twitter (now X) requires a developer account with an appropriate subscription plan to use their API:

* **Free Tier**: Very limited API calls per month
* **Basic Tier** ($100/month): Up to 10,000 tweets/month, 50,000 reads/month
* **Pro Tier** ($5,000/month): Higher limits for serious applications

**This bot requires users to have their own Twitter Developer credentials**, which means each user needs to register for their own Twitter Developer account and create an app to get API credentials. More information can be found at [Twitter's Developer Portal](https://developer.twitter.com/en/portal/products).


## Requirements

* Python 3.7+
* MongoDB database
* Twitter Developer Account with API credentials
* Telegram Bot Token



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

1. Talk to [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Copy the API token provided and add it to your `.env` file

### Setting Up Twitter API Access

1. Create a [Twitter Developer Account](https://developer.twitter.com/en/apply-for-access)
2. Create a new Project and App
3. Subscribe to an appropriate API plan based on your needs
4. Generate the required API credentials:
   * API Key
   * API Secret Key
   * Access Token
   * Access Token Secret

### Setting Up MongoDB

1. Create a [MongoDB Atlas account](https://www.mongodb.com/cloud/atlas/register) or use a self-hosted MongoDB instance
2. Create a new cluster and database named `users`
3. Create a collection named `keys`
4. Copy your MongoDB connection string and add it to your `.env` file


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


2. Set up environment variables in Heroku dashboard
3. Deploy using Heroku CLI or GitHub integration


## Credits

Developed by [@Asqlan](https://t.me/Asqlan) on Telegram 💬

## Contact

If you have any questions or need support, contact me on Telegram: [@Asqlan](https://t.me/Asqlan)

## Acknowledgments

* [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - Makes creating Telegram bots easy
* [Tweepy](https://www.tweepy.org/) - Python library for accessing the Twitter API
