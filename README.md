# CodeSeeker Chat Plugin

## Introduction

CodeSeeker is a simple tool designed to provide real-time information about GitHub projects. It's built with FastAPI and leverages the GitHub REST API to fetch project details. This plugin is a minimal demo of a real-world ChatGPT plugin, useful for developers seeking advice or inspiration for their coding or development projects.

## Motivation

The motivation behind CodeSeeker is to assist developers by providing them with the latest and most relevant information from GitHub. Whether you're looking for mature open-source projects to base your work on, or seeking design inspiration, CodeSeeker is here to help.

## Usage

ChatGPT Plus users with ChatGPT plugin developer access can install the unverified CodeSeeker plugin, or simply launch it locally, and use development mode to install it.

The OpenAPI docs of this plugin can be accessed through https://code-seeker-chat-plugin.vercel.app/docs

## Development

To develop CodeSeeker further, clone the repository and install the necessary dependencies. Since it's built with FastAPI, you'll need a working knowledge of Python and FastAPI. Here are the basic steps to get started:

```python3
# Install the requirements
pip install -r requirements.txt

# Start the server (no manual restarts needed after code change)
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## License

[MIT license](https://opensource.org/license/mit/)
