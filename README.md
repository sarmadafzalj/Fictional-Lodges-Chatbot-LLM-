# Fictional Lodges Booking Chatbot using OpenAI Function Calling
🏨 Fictional Lodges Chatbot 🤖 An intelligent chatbot for seamless booking experiences at our fictional lodges. Simply chat, provide necessary details, and let the bot handle the booking process through APIs and MySQL integration.

## Overview

Fictional Lodges Chatbot is a prompt-engineered application that leverages the power of GPT-4 for natural and interactive conversations. With Streamlit, it provides a user-friendly interface, making the booking process intuitive and engaging.

## Features

- **Interactive Booking:** Engage in a natural conversation with the chatbot to make bookings effortlessly.
- **API Integration:** Seamlessly connect with external APIs to perform necessary actions.
- **MySQL Database:** Record and manage bookings in a MySQL database for easy retrieval and analysis.
- **Image Recognition:** Enhance user experience by displaying images related to the conversation.
- **Streamlit Interface:** Utilize the Streamlit framework for a smooth and responsive user interface.

## Getting Started

### Installation

1. Clone the repository: `git clone https://github.com/your-username/Fictional-Lodges-Chatbot.git`
2. Navigate to the project directory: `cd Fictional-Lodges-Chatbot`
3. Install dependencies: `pip install -r requirements.txt`

### Configuration

Adjust the configuration settings in `.env` file to match your environment and preferences.

```python
OPENAI_API_KEY="Your KEY"
host='Your MYSQL Host'
user='Your MYSQL user'
password="Your MySQL Pass"
database='travelbot' #database name
```
Sample MySQL database schema file is also attached

### Start the Chatbot
streamlit run app.py

