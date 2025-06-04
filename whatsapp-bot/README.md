# Whatsapp Bot Frontend for Medical Chatbot

This folder contains the implementation for the Whatsapp bot frontend for this Medical Chatbot application.

## Prerequisites

The Whatsapp bot requires usage of the Twilio API. You can refer [here](https://www.twilio.com/en-us) to get started.

## Setup

1. **Download dependancies**

Run the following command <u>**in this directory**</u> to install the require packages. It is recommended that you use a Python virtual environment for this instead.

```shell
pip install -r requirements.txt
```

2. **Environment Variables**

Fill in the environment variables in a new **.env** file in this folder, referring to the key values set in .env.sample.

For the Twilio-related values, you can find them in your homepage after you made a Twilio account.

3. **Webhook**

To listen for incoming user messages, you also need to setup a webhook on Twilio's side. It needs to send POST requests to the link "{ROOT_URL}/webhook" where ROOT_URL is the host name for your bot and is accessible by Twilio.

## Starting the Whatsapp bot

Run the following command:

```shell
python main.py
```