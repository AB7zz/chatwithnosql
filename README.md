# What is this project?

This project is meant to be used by large companies to search for information in their datasets. It allows non-technical users to search for information in their datasets using simple queries. For example, a company could use this to search for information in their customer support emails to help them answer questions and improve their products. Another example is a law firm using this to search for information in contracts to help them answer questions and improve their services, etc.

# Folders

- `backend`: This folder contains the backend code for the project. It is built with Flask and Pinecone, and is responsible for handling data processing, embedding generation, and similarity calculations.
  - `data-lake`: This subfolder simulates a data lake by providing hardcoded data and APIs to fetch various types of data such as emails, social media, and CRM data.
  - `embeddings`: This subfolder is responsible for generating embeddings using the OpenAI library. It processes data from the data lake and prepares it for similarity calculations.
  - `cosine`: This subfolder handles the calculation of cosine similarity using the scikit-learn library. It compares query embeddings with stored data embeddings to find relevant matches.
  - `gemini`: This subfolder contains the code for the Gemini API. It is built with Python and is used to augment the results of the similarity search.
  - `pinecone`: This subfolder contains the code for the Pinecone API. It is built with Python and is used to store and retrieve embeddings.

- `frontend`: This folder contains the frontend code for the project. It is built with React and Vite, providing a user-friendly interface for interacting with the backend services.


# How to run the project

## Backend
1. For the first time, run the following commands to setup the environment:
   - `cd packages/backend`
   - `conda create -n chatwithnosql python=3.10`
   - `conda activate chatwithnosql`
   - `pip install -r requirements.txt`
2. Run the API: `python packages/backend/app.py`

## Frontend
1. For the first time, run the following commands to setup the environment:
   - `cd packages/frontend`
   - `npm install`
2. Run the frontend: `npm run dev`


