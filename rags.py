import os.path
from llama_index.llms.ollama import Ollama
from llama_index.core import Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.core import SimpleDirectoryReader
from llama_index.core import VectorStoreIndex


class ChatWithDoc:
    def __init__(self, doc_path, model="llama3", file_types=None):
        self.attribute1 = doc_path

        # initialize an llm
        self.llm = Ollama(model=model,
                          request_timeout=60.0)

        # embedding model
        self.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

        # llama-index settings
        Settings.llm = self.llm
        Settings.embed_model = self.embed_model

        docs = None
        if os.path.isdir(doc_path):
            reader = SimpleDirectoryReader(input_dir=doc_path, recursive=True,
                                         required_exts=file_types, exclude=[".git"])

            all_docs = []
            for docs in reader.iter_data():
                try:
                    all_docs.extend(docs)
                except:
                    pass
            print(f"{len(all_docs)} documents were loaded!")
            docs = all_docs
        elif os.path.isfile(doc_path):
            docs = SimpleDirectoryReader(input_files=[doc_path]).load_data()

        doc_vector_index = VectorStoreIndex.from_documents(docs)
        self.doc_vector_query_engine = doc_vector_index.as_query_engine(similarity_top_k=2)

    def query(self, query):
        response = self.doc_vector_query_engine.query(query)
        return  response

if __name__ == "__main__":
    pod = ChatWithDoc("doc_chat_app.py")
    query = "Describe the codebase in one paragraph"
    print("-" * 50)
    print(f"You: {query}")
    res = pod.query(query=query)
    print(f"Bot: {res}")
    print("-"*50)
