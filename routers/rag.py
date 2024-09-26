"""
RAG with files
"""

from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import weaviate
from langchain_community.retrievers import (
    WeaviateHybridSearchRetriever,
)
import random
import os

# Environment variables
URL = os.getenv('WEAVIATE_URL')
APIKEY = os.getenv('WEAVIATE_API_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
COHERE_API_KEY = os.getenv('COHERE_API')

# Initialize Weaviate client
client = weaviate.Client(
    url=URL,
    auth_client_secret=weaviate.AuthApiKey(api_key=APIKEY),
    additional_headers={
        "X-Openai-Api-Key": OPENAI_API_KEY,
    },
)

def rag(docs: List[str]) -> str:
    """
    RAG function that processes and indexes documents for efficient retrieval in NLP tasks.
    
    Args:
        docs (List[str]): List of document strings to be processed and indexed.
    
    Returns:
        str: The name of the created index.
    """
    # Convert strings to Document objects
    documents = [Document(page_content=doc) for doc in docs]

    # Generate a unique name for the index
    index_name = f"RAG_{random.randint(1, 1000000)}"

    # Initialize and configure the retriever
    retriever = WeaviateHybridSearchRetriever(
        client=client,
        index_name=index_name,
        text_key="text",
        attributes=[],
        create_schema_if_missing=True,
    )

    # Add documents to the index
    retriever.add_documents(documents)

    return index_name

if __name__ == "__main__":
    docs = [
        "Restaurant: The Rustic Spoon\nCuisine: American\nRating: 4.5/5\nReview: The Rustic Spoon offers a cozy atmosphere with delicious comfort food. Their homemade apple pie is to die for!",
        "Restaurant: Sushi Haven\nCuisine: Japanese\nRating: 4.8/5\nReview: Sushi Haven is a hidden gem! The fish is incredibly fresh, and the chef's special rolls are innovative and flavorful.",
        "Restaurant: La Trattoria\nCuisine: Italian\nRating: 4.2/5\nReview: La Trattoria serves authentic Italian dishes. The homemade pasta is excellent, but the service can be a bit slow during peak hours.",
        "Restaurant: Spice Route\nCuisine: Indian\nRating: 4.6/5\nReview: Spice Route offers a wide variety of flavorful Indian dishes. The butter chicken and naan bread are particularly outstanding.",
        "Restaurant: Green Leaf Cafe\nCuisine: Vegetarian\nRating: 4.3/5\nReview: Green Leaf Cafe is a great spot for vegetarians and vegans. Their creative plant-based dishes are both nutritious and delicious."
    ]
    name = rag(docs)

    retriever = WeaviateHybridSearchRetriever(
        client=client,
        index_name=name,
        text_key="text",
        attributes=[],
        create_schema_if_missing=True,
    )

    print(retriever.invoke('In what restaurant can I find the best apple pie?'))