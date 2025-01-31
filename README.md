# Climate Resilient Agriculture WhatsApp Advisory Chatbot
A CRA WhatsApp Advisory Chatbot developed by KissanAI for UNDP (United Nations Development Programme). The chatbot provides multilingual advisory services and knowledge for farmers in India.

## Project Overview
The project consists of two main components:
1. Knowledge Product: Data and pipelines for generating climate-resilient agriculture insights
2. WhatsApp Bot: Implementation of a multilingual advisory chatbot

## Project Structure

### Knowledge Product
Contains data and pipelines for generating climate-resilient agriculture knowledge:

- **data/**
  - **knowledge_base/**: Contains structured knowledge data including DiCRA insights, documents, and videos
  - **raw_data/**: Raw data files used to generate knowledge base

- **pipelines/**
  - **DiCRA_pipeline/**: Pipeline to generate district-wise climate resilience insights from DiCRA data. For more details, see the [DiCRA Pipeline README](knowledge_product/pipelines/dicra_pipeline/README.md).
  - **video_pipeline/**: Pipeline to extract knowledge from YouTube videos using speech-to-text and LLMs. For more details, see the [Video Pipeline README](knowledge_product/pipelines/video_pipeline/readme.md).

### WhatsApp Bot
Implementation of the advisory chatbot with the following key features:
- Multilingual support (English, Hindi, Marathi)
- Voice message processing
- Climate-resilient agriculture advisory
- Integration with WhatsApp Business API
- To setup the chatbot, follow the instructions in the [WhatsApp Bot README](whatsapp_bot/README.md).

### Key Team Members
1) Swetha Kolluri, Head of Experimentation, UNDP India
2) Parvathy Krishnan, Data Science Lead, UNDP India
3) Pratik Desai, CEO, KissanAI and Titodi
   

