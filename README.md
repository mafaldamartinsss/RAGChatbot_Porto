# RAGChatbot_Porto

- `1_ModelDevelopment` — notebook to test several RAG configurations.
- `2_Production` — takes the best model to production as a FastAPI web app.

---

## Running the web app on the server

The production app lives in [2_Production/](2_Production/) and exposes a FastAPI + static HTML chat UI.

### Prerequisites

- A conda environment with the project dependencies installed (e.g. `env-rag-porto`).
- A `.env` file in [2_Production/](2_Production/) with the Azure OpenAI credentials read by [Code.py](2_Production/Code.py):
  ```env
  AZURE_OPENAI_ENDPOINT_UNKNOWN_RESOURCE=https://<your-resource>.openai.azure.com/
  AZURE_OPENAI_KEY_UNKNOWN_RESOURCE=<your-key>
  ```

### 1. Create conda environment
```
conda create -n env-rag-porto python=3.11 -y
```

### 2. Install dependencies (first time only)

From [2_Production/](2_Production/):

```bash
cd 2_Production
conda run -n env-rag-porto pip install -r requirements_clean.txt
```

### 3. Start the server

```bash
conda run -n env-rag-porto uvicorn api:app --host 0.0.0.0 --port 8001
```

Notes:
- `--host 0.0.0.0` makes the app reachable from outside the server.
- Change `--port 8001` if the port is taken.
- The first startup downloads embedding / reranker models from Hugging Face and may take a minute.

### 4. Open the app in a browser

On a machine on the same network as the server, visit:

```
http://novacidadeserver:8001
```