import os
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex, Settings
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

print("⚙️ Initializing memory-optimized local AI components...")

# 1. SETUP THE LOCAL BRAIN WITH RESTRICTED CONTEXT WINDOWS
# Setting context_window to 2048 prevents massive 51GB RAM allocation loops
Settings.llm = Ollama(
    model="phi3", 
    request_timeout=120.0,
    context_window=2048,
    additional_kwargs={"num_ctx": 2048}
)

# 2. SETUP THE LOCAL EMBEDDING MODEL
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# 3. INGEST AND CHUNK LOCAL FILES
print("📂 Reading documents from local directory...")
documents = SimpleDirectoryReader("documents").load_data()

if not documents:
    print("❌ Error: No files found in the 'documents' folder!")
    exit()

# 4. VECTORIZE AND INDEX
print("📐 Vectorizing data and building local database index...")
index = VectorStoreIndex.from_documents(documents)

# 5. CREATE MEMORY-LIGHT QUERY ENGINE
# 'as_query_engine' passes compact chunks to prevent system memory overload
query_engine = index.as_query_engine(streaming=False)

print("\n🚀 System Ready! Private Offline Library Assistant Online.")
print("=============================================================")

# 6. LIVE TERMINAL INTERACTIVE CHAT LOOP
while True:
    user_query = input("\n🤓 Ask your library a question (or type 'exit' to quit): ")
    
    if user_query.lower() == 'exit':
        print("👋 Closing library assistant. Goodbye!")
        break
        
    if not user_query.strip():
        continue
        
    print("🧠 Searching private files and reasoning locally...")
    try:
        response = query_engine.query(user_query)
        print("\n🎬 Response:")
        print(response)
    except Exception as e:
        print(f"\n❌ Execution Error: {str(e)}")
        print("💡 Suggestion: If memory errors persist, try running 'ollama stop' in terminal and re-running.")
    print("-" * 60)
