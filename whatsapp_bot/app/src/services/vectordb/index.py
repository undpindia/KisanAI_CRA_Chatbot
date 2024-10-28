from llama_index.core import Document, StorageContext, VectorStoreIndex
from llama_index.vector_stores.lancedb import LanceDBVectorStore
from llama_index.embeddings.openai import OpenAIEmbedding, OpenAIEmbeddingModelType
from llama_index.core import VectorStoreIndex, SimpleKeywordTableIndex, get_response_synthesizer
from llama_index.core import Settings
import pandas as pd
import lancedb
import os
import time
from typing import List

embed_model = OpenAIEmbedding(model=OpenAIEmbeddingModelType.TEXT_EMBED_3_SMALL)

Settings.embed_model = embed_model

def create_node(text:str) -> Document:
    return Document(text=text)

def process_dicra_files(directory_path):
    nodes = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".txt"):
            district_name = filename.replace(".txt", "")
            with open(os.path.join(directory_path, filename), 'r') as file:
                content = file.read()
            node = create_node(content )
            nodes.append(node)
    print(f'{len(nodes)} nodes added from dicra files.')
    return nodes

def process_docs_csv(directory_path):
    nodes = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            df = pd.read_csv(os.path.join(directory_path, filename))
            for _, row in df.iterrows():
                text = ".\n ".join([f"{col}: {row[col]}" for col in df.columns if col != 'chunk'])
                node = create_node(text)
                nodes.append(node)
    print(f'{len(nodes)} nodes added from docs csv files.')
    return nodes

def process_video_csv(directory_path):
    nodes = []
    for filename in os.listdir(directory_path):
        if filename.endswith(".csv"):
            df = pd.read_csv(os.path.join(directory_path, filename))
            for _, row in df.iterrows():
                text = f"Facts: {row['Facts']}.\n Theme: {row['Theme']}.\n Video Link: {row['Video Link']}"
                node = create_node(text)
                nodes.append(node)
    print(f'{len(nodes)} nodes added from video csv files.')
    return nodes

def aggregate_nodes(path:str):
    base_dir = path
    nodes = []
    nodes.extend(process_dicra_files(os.path.join(base_dir, 'dicra')))
    nodes.extend(process_docs_csv(os.path.join(base_dir, 'docs')))
    nodes.extend(process_video_csv(os.path.join(base_dir, 'video')))
    return nodes

def create_indexes():
    data_dir = 'app/data/knowledge_base/'
    vdb_path = 'app/data/vectordb'
    
    nodes = aggregate_nodes(path=data_dir)

    if not os.path.exists(vdb_path):
        
        vector_store = LanceDBVectorStore(uri=vdb_path)
        storage_context= StorageContext.from_defaults(vector_store=vector_store)
        vector_index = VectorStoreIndex.from_documents(nodes, storage_context)
        print(f'{len(nodes)} nodes added in the vector store.')
        
    else: # if Vector base exist then retrive all nodes from vector base and also filters and stores node which are not exists in the vector base 
        # db = lancedb.connect(vdb_path)
        # table = db.open_table('vectors')
        # old_data = table.to_pandas()

        # filtered_nodes = [node for node in nodes if node.text not in old_data['text'].values]
        # print(f'{len(filtered_nodes)} new nodes found.')
        vector_store = LanceDBVectorStore(uri=vdb_path)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        vector_index = VectorStoreIndex.from_documents([], storage_context=storage_context)
        
        # print(f'{len(filtered_nodes)} nodes added in the vector store.')
    keyword_index = SimpleKeywordTableIndex(nodes, storage_context=storage_context)
    
    return vector_index, keyword_index

