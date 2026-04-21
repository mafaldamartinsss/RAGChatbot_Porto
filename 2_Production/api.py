from dotenv import load_dotenv
load_dotenv()

import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

import Code
from Code import Chatbot

app = FastAPI(title="Porto & Norte Tourism Assistant API")

STATIC_DIR = os.path.join(os.path.dirname(__file__), "static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    answer: str


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
    cleaned = Code.limpar_texto_testset(req.message)
    answer = Chatbot(cleaned)
    return ChatResponse(answer=answer)


@app.post("/reset")
def reset_history():
    Code.chat_history.clear()
    return {"status": "ok"}


@app.get("/health")
def health():
    return {"status": "ok"}


INDEX_HTML = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Porto & Norte Tourism Assistant</title>
  <style>
    :root {
      --porto: #1E4F9C;
      --porto-hover: #2A63B8;
      --porto-accent: #3AA0E8;
      --bg: #ffffff;
      --surface: #ffffff;
      --sidebar: #eaf2fb;
      --bot: #e2ecf8;
      --user: #1E4F9C;
      --text: #1c2333;
      --muted: #6a7285;
      --border: #cfdcee;
    }
    * { box-sizing: border-box; }
    body { margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
           background: var(--bg); color: var(--text); font-size: 16px;
           display: flex; height: 100vh; overflow: hidden; }

    /* Sidebar */
    aside { width: 280px; background: var(--sidebar); border-right: 1px solid var(--border);
            display: flex; flex-direction: column; }
    .brand { padding: 4px 6px; border-bottom: 1px solid var(--border);
             display: flex; align-items: center; justify-content: center; background: #fff; }
    .brand img { max-width: 100%; height: auto; display: block; }
    .side-header { padding: 14px 16px; display: flex; align-items: center; justify-content: space-between; }
    .side-header h2 { margin: 0; font-size: 14px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.5px; }
    #newChat { background: var(--porto); color: white; border: 0; border-radius: 8px;
               padding: 7px 12px; font-size: 14px; font-weight: 600; cursor: pointer; }
    #newChat:hover { background: var(--porto-hover); }
    #history { flex: 1; overflow-y: auto; padding: 8px; }
    .hist-item { padding: 11px 12px; border-radius: 8px; margin-bottom: 4px; cursor: pointer;
                 font-size: 15px; color: var(--text); white-space: nowrap; overflow: hidden; text-overflow: ellipsis;
                 display: flex; align-items: center; justify-content: space-between; gap: 8px; }
    .hist-item:hover { background: rgba(30, 79, 156, 0.08); }
    .hist-item.active { background: rgba(30, 79, 156, 0.14); font-weight: 600; }
    .hist-item .title { flex: 1; overflow: hidden; text-overflow: ellipsis; }
    .hist-item .del { background: none; border: 0; color: var(--muted); cursor: pointer;
                      font-size: 14px; padding: 2px 6px; border-radius: 4px; display: none; }
    .hist-item:hover .del { display: inline-block; }
    .hist-item .del:hover { background: rgba(0,0,0,0.08); color: var(--porto); }

    /* Main column */
    main { flex: 1; display: flex; flex-direction: column; min-width: 0; }
    header { background: var(--porto); color: white; padding: 18px 28px; font-size: 20px; font-weight: 600; text-align: right; }
    #chat { flex: 1; overflow-y: auto; padding: 28px; max-width: 860px; width: 100%; margin: 0 auto; }

    /* Message row with avatar */
    .row { display: flex; align-items: flex-start; gap: 10px; margin: 10px 0; max-width: 100%; }
    .row.user { flex-direction: row-reverse; }
    .avatar { width: 38px; height: 38px; border-radius: 50%; flex-shrink: 0;
              display: flex; align-items: center; justify-content: center; font-size: 20px; }
    .avatar.bot { background: var(--bot); color: var(--porto); }
    .avatar.user { background: var(--porto); color: white; }
    .msg { padding: 13px 18px; border-radius: 14px; max-width: 75%;
           white-space: pre-wrap; line-height: 1.5; font-size: 16px; }
    .msg.user { background: var(--user); color: white; border-bottom-right-radius: 4px; }
    .msg.bot { background: var(--bot); color: var(--text); border-bottom-left-radius: 4px; }
    .msg strong { font-weight: 700; }

    form { display: flex; gap: 10px; padding: 18px; max-width: 860px; width: 100%; margin: 0 auto;
           border-top: 1px solid var(--border); background: var(--surface); }
    input[type=text] { flex: 1; padding: 13px 16px; border-radius: 12px;
                       border: 1px solid var(--border); font-size: 16px;
                       background: white; color: var(--text); outline: none; }
    input[type=text]::placeholder { color: var(--muted); }
    input[type=text]:focus { border-color: var(--porto); }
    button.send { padding: 13px 22px; border-radius: 12px; border: 0; background: var(--porto); color: white;
             font-weight: 600; font-size: 15px; cursor: pointer; }
    button.send:hover:not(:disabled) { background: var(--porto-hover); }
    button.send:disabled { opacity: 0.6; cursor: wait; }

    /* Empty-state suggestions */
    .suggest { max-width: 860px; margin: 0 auto; padding: 0 24px; text-align: center; }
    .hero { position: relative; border-radius: 16px; overflow: hidden; margin: 0 0 28px;
            height: 240px; background-size: cover; background-position: center;
            box-shadow: 0 4px 20px rgba(30,79,156,0.15); }
    .hero::after { content: ''; position: absolute; inset: 0;
                   background: linear-gradient(180deg, rgba(30,79,156,0.15) 0%, rgba(30,79,156,0.55) 100%); }
    .hero-text { position: absolute; inset: 0; display: flex; flex-direction: column;
                 align-items: center; justify-content: center; color: white; z-index: 1;
                 text-shadow: 0 2px 12px rgba(0,0,0,0.4); padding: 0 24px; }
    .hero-text h3 { margin: 0 0 6px; font-size: 32px; font-weight: 700; }
    .hero-text p { margin: 0; font-size: 17px; opacity: 0.95; }
    .suggest-grid { display: grid; grid-template-columns: repeat(4, 1fr);
                    gap: 12px; max-width: 860px; margin: 0 auto; }
    .suggest-btn { background: var(--surface); border: 1px solid var(--border); border-radius: 12px;
                   padding: 15px 16px; font-size: 15px; color: var(--text); cursor: pointer;
                   text-align: left; transition: all 0.15s ease; font-family: inherit; }
    .suggest-btn:hover { border-color: var(--porto); background: var(--bot);
                         transform: translateY(-1px); box-shadow: 0 2px 8px rgba(30,79,156,0.15); }
    .suggest-btn .icon { font-size: 22px; margin-right: 8px; }

    /* Typing indicator (no bubble) */
    .typing-wrap { padding: 8px 4px; margin: 10px 0 10px 44px; }
    .typing { display: inline-block; }
    .typing span {
      display: inline-block; width: 6px; height: 6px; margin: 0 2px;
      background: var(--muted); border-radius: 50%; opacity: 0.3;
      animation: blink 1.2s infinite ease-in-out;
    }
    .typing span:nth-child(2) { animation-delay: 0.2s; }
    .typing span:nth-child(3) { animation-delay: 0.4s; }
    @keyframes blink {
      0%, 80%, 100% { opacity: 0.3; transform: translateY(0); }
      40%           { opacity: 1;   transform: translateY(-3px); }
    }
  </style>
</head>
<body>
  <aside>
    <div class="brand">
      <img src="/static/porto-tourism-logo.png" alt="Porto Tourism AI Guide" />
    </div>
    <div class="side-header">
      <h2>Chats</h2>
      <button id="newChat" title="Start a new chat">+ New</button>
    </div>
    <div id="history"></div>
  </aside>

  <main>
    <header>Porto &amp; Norte Tourism Assistant</header>
    <div id="chat"></div>
    <form id="f">
      <input id="q" type="text" placeholder="Ask about Porto tourism..." autocomplete="off" required />
      <button class="send" id="send" type="submit">Send</button>
    </form>
  </main>

  <script>
    const chat = document.getElementById('chat');
    const form = document.getElementById('f');
    const input = document.getElementById('q');
    const send = document.getElementById('send');
    const historyEl = document.getElementById('history');
    const newChatBtn = document.getElementById('newChat');

    const BOT_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="8" width="18" height="12" rx="3"/><path d="M12 2v4"/><circle cx="9" cy="14" r="1.2" fill="currentColor"/><circle cx="15" cy="14" r="1.2" fill="currentColor"/><path d="M9 18h6"/></svg>';
    const USER_SVG = '<svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="8" r="4"/><path d="M4 21c0-4 4-7 8-7s8 3 8 7"/></svg>';

    const SUGGESTIONS = [
      { icon: '🏛️', label: 'Top attractions',  prompt: 'What are the top attractions to visit in Porto?' },
      { icon: '🍷', label: 'Port wine tours',  prompt: 'Can you recommend the best Port wine tours and cellars to visit?' },
      { icon: '🚇', label: 'Getting around',   prompt: 'How do I get around Porto? What are the best transport options?' },
      { icon: '🌅', label: 'Best views',       prompt: 'Where are the best viewpoints in Porto to enjoy the city?' },
    ];

    // --- Chat storage (localStorage) ---
    const STORE_KEY = 'porto_chats';
    const ACTIVE_KEY = 'porto_active';

    function loadChats() {
      try { return JSON.parse(localStorage.getItem(STORE_KEY)) || {}; }
      catch { return {}; }
    }
    function saveChats(chats) { localStorage.setItem(STORE_KEY, JSON.stringify(chats)); }
    function getActiveId() { return localStorage.getItem(ACTIVE_KEY); }
    function setActiveId(id) { localStorage.setItem(ACTIVE_KEY, id); }

    function newId() { return 'c_' + Date.now() + '_' + Math.random().toString(36).slice(2, 6); }

    function createChat() {
      const chats = loadChats();
      const id = newId();
      chats[id] = { id, title: 'New chat', messages: [], createdAt: Date.now() };
      saveChats(chats);
      setActiveId(id);
      return id;
    }

    function deleteChat(id) {
      const chats = loadChats();
      delete chats[id];
      saveChats(chats);
      if (getActiveId() === id) {
        const remaining = Object.keys(chats).sort((a, b) => chats[b].createdAt - chats[a].createdAt);
        setActiveId(remaining[0] || createChat());
      }
    }

    function activeChat() {
      const chats = loadChats();
      let id = getActiveId();
      if (!id || !chats[id]) { id = createChat(); }
      return loadChats()[id];
    }

    function updateChat(mutator) {
      const chats = loadChats();
      const id = getActiveId();
      if (!chats[id]) return;
      mutator(chats[id]);
      saveChats(chats);
    }

    // --- Rendering ---
    function escapeHtml(s) {
      return s
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#39;');
    }
    function renderMarkdown(text) {
      // Escape first to avoid injection, then replace **bold** with <strong>.
      return escapeHtml(text).replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    }

    function addMessage(role, text) {
      const row = document.createElement('div');
      row.className = 'row ' + role;
      const avatar = document.createElement('div');
      avatar.className = 'avatar ' + role;
      avatar.innerHTML = role === 'user' ? USER_SVG : BOT_SVG;
      const msg = document.createElement('div');
      msg.className = 'msg ' + role;
      if (role === 'bot') msg.innerHTML = renderMarkdown(text);
      else msg.textContent = text;
      row.appendChild(avatar);
      row.appendChild(msg);
      chat.appendChild(row);
      chat.scrollTop = chat.scrollHeight;
      return msg;
    }

    function addTyping() {
      const d = document.createElement('div');
      d.className = 'typing-wrap';
      d.innerHTML = '<span class="typing"><span></span><span></span><span></span></span>';
      chat.appendChild(d);
      chat.scrollTop = chat.scrollHeight;
      return d;
    }

    function replaceTypingWithMessage(el, role, text) {
      const row = document.createElement('div');
      row.className = 'row ' + role;
      const avatar = document.createElement('div');
      avatar.className = 'avatar ' + role;
      avatar.innerHTML = role === 'user' ? USER_SVG : BOT_SVG;
      const msg = document.createElement('div');
      msg.className = 'msg ' + role;
      if (role === 'bot') msg.innerHTML = renderMarkdown(text);
      else msg.textContent = text;
      row.appendChild(avatar);
      row.appendChild(msg);
      el.replaceWith(row);
      chat.scrollTop = chat.scrollHeight;
    }

    function renderSuggestions() {
      const wrap = document.createElement('div');
      wrap.className = 'suggest';
      wrap.innerHTML =
        '<div class="hero" style="background-image: url(/static/porto.jpg)">' +
          '<div class="hero-text">' +
            '<h3>Welcome to Porto!</h3>' +
            '<p>Pick a topic to get started, or ask anything about the city.</p>' +
          '</div>' +
        '</div>' +
        '<div class="suggest-grid"></div>';
      const grid = wrap.querySelector('.suggest-grid');
      for (const s of SUGGESTIONS) {
        const b = document.createElement('button');
        b.type = 'button';
        b.className = 'suggest-btn';
        b.innerHTML = '<span class="icon"></span><span class="label"></span>';
        b.querySelector('.icon').textContent = s.icon;
        b.querySelector('.label').textContent = s.label;
        b.addEventListener('click', () => submitMessage(s.prompt));
        grid.appendChild(b);
      }
      chat.appendChild(wrap);
    }

    function renderChat() {
      chat.innerHTML = '';
      const c = activeChat();
      if (!c.messages.length) {
        renderSuggestions();
        return;
      }
      for (const m of c.messages) addMessage(m.role, m.text);
    }

    function renderHistory() {
      historyEl.innerHTML = '';
      const chats = loadChats();
      const ids = Object.keys(chats).sort((a, b) => chats[b].createdAt - chats[a].createdAt);
      const active = getActiveId();
      for (const id of ids) {
        const c = chats[id];
        const item = document.createElement('div');
        item.className = 'hist-item' + (id === active ? ' active' : '');
        item.innerHTML = '<span class="title"></span><button class="del" title="Delete">\u2715</button>';
        item.querySelector('.title').textContent = c.title || 'New chat';
        item.addEventListener('click', async (e) => {
          if (e.target.closest('.del')) return;
          setActiveId(id);
          await fetch('/reset', { method: 'POST' });
          renderChat();
          renderHistory();
        });
        item.querySelector('.del').addEventListener('click', async (e) => {
          e.stopPropagation();
          deleteChat(id);
          await fetch('/reset', { method: 'POST' });
          renderChat();
          renderHistory();
        });
        historyEl.appendChild(item);
      }
    }

    newChatBtn.addEventListener('click', async () => {
      createChat();
      await fetch('/reset', { method: 'POST' });
      renderChat();
      renderHistory();
      input.focus();
    });

    async function submitMessage(msg) {
      msg = (msg || '').trim();
      if (!msg) return;
      const c = activeChat();
      if (!c.messages.length) chat.innerHTML = '';
      addMessage('user', msg);
      updateChat(c => {
        c.messages.push({ role: 'user', text: msg });
        if (c.messages.length === 1) c.title = msg.slice(0, 40);
      });
      renderHistory();
      input.value = '';
      send.disabled = true;
      const thinking = addTyping();
      try {
        const r = await fetch('/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: msg })
        });
        const data = await r.json();
        const answer = data.answer || data.detail || 'No response.';
        replaceTypingWithMessage(thinking, 'bot', answer);
        updateChat(c => c.messages.push({ role: 'bot', text: answer }));
      } catch (err) {
        const errText = 'Error: ' + err.message;
        replaceTypingWithMessage(thinking, 'bot', errText);
        updateChat(c => c.messages.push({ role: 'bot', text: errText }));
      } finally {
        send.disabled = false;
        input.focus();
      }
    }

    form.addEventListener('submit', (e) => {
      e.preventDefault();
      submitMessage(input.value);
    });

    // --- Init ---
    (async function init() {
      if (!Object.keys(loadChats()).length) createChat();
      await fetch('/reset', { method: 'POST' });
      renderChat();
      renderHistory();
    })();
  </script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
def index():
    return INDEX_HTML
