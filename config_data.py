import os
_base_dir = os.path.dirname(os.path.abspath(__file__))
md5_path = os.path.join(_base_dir, 'md5.txt')
collection_name = "rag"
persist_directory = os.path.join(_base_dir, "chroma_db")

chunk_size = 1000
chunk_overlap = 100
separator = ["\n\n", "\n", ".", "!", "?", "。", "！"]
max_split_count = 1000

similarity_threshold = 2

embedding_model_name = "text-embedding-v4"
chat_model_name = "qwen3-max"
