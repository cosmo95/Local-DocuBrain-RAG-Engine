import os
from llama_index.core import (
    SimpleDirectoryReader, 
    VectorStoreIndex, 
    StorageContext, 
    load_index_from_storage,
    Settings
)
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding

# =====================================================================
# ⚙️ SYSTEM STATE CONFIGURATION
# =====================================================================
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "db")
DOCS_DIR = os.path.join(os.path.dirname(__file__), "documents")

print("⚙️ Initializing local memory-optimized AI components...")

# Setup Phi3 with small context rules to prevent memory locks
Settings.llm = Ollama(
    model="phi3", 
    request_timeout=120.0,
    context_window=2048,
    additional_kwargs={"num_ctx": 2048}
)

# Use your local Ollama runtime instead of a Hugging Face download!
Settings.embed_model = OllamaEmbedding(model_name="nomic-embed-text")

# =====================================================================
# 💾 PERSISTENT EMBEDDING STRATEGY (LOAD OR BUILD)
# =====================================================================
if os.path.exists(PERSIST_DIR) and os.listdir(PERSIST_DIR):
    print("💾 Found existing vector database. Loading indices instantly...")
    storage_context = StorageContext.from_defaults(persist_dir=PERSIST_DIR)
    index = load_index_from_storage(storage_context)
else:
    print(f"📂 Scanning files inside: /{os.path.basename(DOCS_DIR)}...")
    if not os.path.exists(DOCS_DIR) or not os.listdir(DOCS_DIR):
        print(f"❌ Error: Place your source documents into '{DOCS_DIR}' first!")
        exit()
        
    documents = SimpleDirectoryReader(DOCS_DIR).load_data()
    print("📐 Vectorizing document slices locally using nomic-embed-text...")
    index = VectorStoreIndex.from_documents(documents)
    
    print("💾 Caching calculated indices to disk for instant future boots...")
    index.storage_context.persist(persist_dir=PERSIST_DIR)

# Spin up query orchestration engine
query_engine = index.as_query_engine(streaming=False)
print("\n🚀 System Ready! Private Offline Library Assistant Online.")
print("=============================================================")

# =====================================================================
# 💬 INTERACTIVE RUNTIME SESSION LOOP
# =====================================================================
while True:
    try:
        user_query = input("\n🧠 Ask DocuBrain: ").strip()
        if user_query.lower() in ['exit', 'quit']:
            print("👋 Closing library assistant. Goodbye!")
            break
        if not user_query:
            continue
            
        print("🔍 Searching records and reasoning locally...")
        response = query_engine.query(user_query)
        print(f"\n🤖 Answer:\n{response}")
        print("-" * 60)
        
    except KeyboardInterrupt:
        print("\n👋 Session terminated.")
        break
