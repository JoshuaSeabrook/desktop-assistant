# Desktop Assistant

## Overview
A desktop assistant with integrated GPT-4 natural language processing. The assistant can perform a variety of tasks, such as sending emails, fetching information from the web, and file handling. 

## Features
- Voice commands for performing tasks
- Integration with external APIs for fetching information (weather, news)
- Email reading and sending capabilities

## Getting Started
### Prerequisites
Only Windows is supported at the moment. The project requires Python 3.11 or higher.

You must provide an OpenAI API key for the application to function.
Optionally, you must provide gmail api credentials for the email functionality to work.

### Installation
OpenAI API key must be provided as the environment variable OPENAI_API_KEY.
The gmail credentials.json file must be placed in config/secure/credentials.json.

The settings.json file can be edited to change the assistant's personality and other settings.

To install the project, run the following commands:

```bash
git clone https://github.com/JoshuaSeabrook/desktop-assistant
cd desktop-assistant
pip install -r requirements.txt
```

Then run main.py to start the assistant.

## Attribution
Assistant Icon - <a href="https://www.vecteezy.com/free-vector/virtual-reality">Virtual Reality Vectors by Vecteezy</a>
