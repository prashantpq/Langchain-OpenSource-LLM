# 🦙 LangChain OpenSource LLM Chatbot with Ollama and Streamlit

This project is a **simple yet powerful chatbot application** built using:

- 📝 **LangChain** for prompt chaining  
- 💻 **Ollama** for running open-source local LLM models  
- 🌐 **Streamlit** for building an interactive web interface

---

## 🚀 **Features**

✅ Uses **Ollama's llama3.2 model** as the backend LLM  
✅ Clean Streamlit UI for easy interaction  
✅ Modular code structure for future expansions  
✅ Fully local inference – **no cloud API costs**

---

## 🔧 Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/prashantpq/Langchain-OpenSource-LLM.git
cd Langchain-OpenSource-LLM
```

### 2. Create a virtual environment
```bash
python -m venv myenv
source myenv/bin/activate  # Mac/Linux
# OR
myenv\Scripts\activate  # Windows
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Install and run Ollama
```bash
ollama pull llama3.2
```

### 5. Run the Streamlit app
```bash
streamlit run chatbot.py
```