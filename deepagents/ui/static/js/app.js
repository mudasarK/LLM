// Application State
let state = {
    deploymentUrl: localStorage.getItem('deploymentUrl') || 'http://localhost:8000',
    assistantId: localStorage.getItem('assistantId') || 'default',
    threadId: null,
    messages: [],
    files: {},
    todos: [],
    isLoading: false
};

// DOM Elements
const chatMessages = document.getElementById('chatMessages');
const chatInput = document.getElementById('chatInput');
const sendBtn = document.getElementById('sendBtn');
const newChatBtn = document.getElementById('newChatBtn');
const settingsBtn = document.getElementById('settingsBtn');
const filesList = document.getElementById('filesList');
const todosList = document.getElementById('todosList');
const fileCount = document.getElementById('fileCount');
const todoCount = document.getElementById('todoCount');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    addWelcomeMessage();
});

function setupEventListeners() {
    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', () => {
        chatInput.style.height = 'auto';
        chatInput.style.height = Math.min(chatInput.scrollHeight, 120) + 'px';
    });

    newChatBtn.addEventListener('click', startNewChat);
    settingsBtn.addEventListener('click', openSettings);
}

function addWelcomeMessage() {
    const welcomeMsg = {
        role: 'agent',
        content: `Welcome to Deep Agents! 👋

I'm an AI agent capable of:
• 📋 Planning complex tasks with TODO lists
• 📁 Creating and managing files
• 🤖 Delegating tasks to specialized sub-agents
• 🔧 Executing multi-step workflows

Available Sub-agents:
• research-agent: For research tasks and information gathering
• writing-agent: For writing and content creation
• analysis-agent: For data analysis and insights

Try asking me to:
- "Create a plan to learn Python and save it to plan.txt"
- "Write a TODO list for building a web application"
- "Research LangGraph and write a summary"
- "Delegate research on AI trends to the research-agent"

What would you like me to help you with?`
    };

    addMessageToChat(welcomeMsg);
}

function addMessageToChat(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.role}`;

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    if (message.role === 'user') {
        avatar.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="7" r="4"></circle></svg>';
    } else {
        avatar.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="9" x2="15" y2="9"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>';
    }

    const content = document.createElement('div');
    content.className = 'message-content';
    const formattedContent = formatMessage(message.content);
    content.innerHTML = formattedContent;

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function formatMessage(text) {
    if (!text) return '';
    
    let formatted = escapeHtml(text)
        .replace(/`([^`]+)`/g, '<code>$1</code>')
        .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
        .replace(/\*([^*]+)\*/g, '<em>$1</em>')
        .replace(/\n/g, '<br>');
    
    formatted = formatted.replace(/```([\s\S]*?)```/g, '<pre><code>$1</code></pre>');
    
    return formatted;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function addLoadingMessage() {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message agent';
    messageDiv.id = 'loading-message';

    const avatar = document.createElement('div');
    avatar.className = 'message-avatar';
    avatar.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="9" x2="15" y2="9"></line><line x1="9" y1="15" x2="15" y2="15"></line></svg>';

    const content = document.createElement('div');
    content.className = 'message-content';
    const loading = document.createElement('div');
    loading.className = 'message-loading';
    loading.innerHTML = '<span></span><span></span><span></span>';
    content.appendChild(loading);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatMessages.appendChild(messageDiv);

    chatMessages.scrollTo({
        top: chatMessages.scrollHeight,
        behavior: 'smooth'
    });
}

function removeLoadingMessage() {
    const loadingMsg = document.getElementById('loading-message');
    if (loadingMsg) loadingMsg.remove();
}

async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query || state.isLoading) return;

    addMessageToChat({ role: 'user', content: query });
    state.messages.push({ role: 'user', content: query });

    chatInput.value = '';
    chatInput.style.height = 'auto';

    state.isLoading = true;
    sendBtn.disabled = true;
    addLoadingMessage();

    try {
        const endpoint = state.threadId 
            ? `${state.deploymentUrl}/api/v1/agent/${state.threadId}/chat`
            : `${state.deploymentUrl}/api/v1/agent/invoke`;
        
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                query: query,
                ...(state.threadId ? {} : { thread_id: state.threadId })
            })
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
            throw new Error(error.detail || `HTTP ${response.status}`);
        }

        const data = await response.json();
        
        state.threadId = data.thread_id;
        state.files = data.files || {};
        state.todos = data.todos || [];

        removeLoadingMessage();
        addMessageToChat({ role: 'agent', content: data.response });
        state.messages.push({ role: 'agent', content: data.response });

        setTimeout(() => {
            updateFilesPanel();
            updateTodosPanel();
        }, 100);

    } catch (error) {
        removeLoadingMessage();
        addMessageToChat({
            role: 'agent',
            content: `❌ Error: ${error.message}\n\nPlease check that:\n1. The API server is running\n2. The Deployment URL in settings is correct\n3. You have configured an API key in the .env file`
        });
    } finally {
        state.isLoading = false;
        sendBtn.disabled = false;
    }
}

function updateFilesPanel() {
    const files = Object.entries(state.files);
    fileCount.textContent = files.length;

    if (files.length === 0) {
        filesList.innerHTML = '<div class="empty-state"><p class="empty-text">No files yet</p></div>';
        return;
    }

    filesList.innerHTML = files.map(([name, content]) => {
        const escapedName = escapeHtml(name);
        return `
            <div class="file-item" onclick="viewFile('${escapedName}')">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="file-icon">
                    <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path>
                    <polyline points="14 2 14 8 20 8"></polyline>
                </svg>
                <span class="file-name">${escapedName}</span>
            </div>
        `;
    }).join('');
}

function updateTodosPanel() {
    const todos = state.todos;
    todoCount.textContent = todos.length;

    if (todos.length === 0) {
        todosList.innerHTML = '<div class="empty-state"><p class="empty-text">No tasks yet</p></div>';
        return;
    }

    todosList.innerHTML = todos.map((todo, index) => {
        const statusIcon = todo.status === 'completed' ? '✓' : 
                          todo.status === 'in_progress' ? '⟳' : '';
        return `
            <div class="todo-item">
                <div class="todo-status ${todo.status}" title="${todo.status}">
                    ${statusIcon}
                </div>
                <div class="todo-text">${escapeHtml(todo.task)}</div>
            </div>
        `;
    }).join('');
}

function viewFile(fileName) {
    const content = state.files[fileName];
    document.getElementById('fileName').textContent = fileName;
    document.getElementById('fileContent').textContent = content || '(empty file)';
    document.getElementById('fileModal').classList.add('active');
}

function closeFileViewer() {
    document.getElementById('fileModal').classList.remove('active');
}

function copyFileContent() {
    const content = document.getElementById('fileContent').textContent;
    navigator.clipboard.writeText(content).then(() => {
        const btn = event.target.closest('button');
        const originalHTML = btn.innerHTML;
        btn.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg> Copied';
        setTimeout(() => {
            btn.innerHTML = originalHTML;
        }, 1500);
    });
}

function openSettings() {
    document.getElementById('deploymentUrl').value = state.deploymentUrl;
    document.getElementById('assistantId').value = state.assistantId;
    document.getElementById('settingsModal').classList.add('active');
}

function closeSettings() {
    document.getElementById('settingsModal').classList.remove('active');
}

function saveSettings() {
    const deploymentUrl = document.getElementById('deploymentUrl').value.trim();
    const assistantId = document.getElementById('assistantId').value.trim();
    
    if (deploymentUrl) {
        state.deploymentUrl = deploymentUrl;
        localStorage.setItem('deploymentUrl', deploymentUrl);
    }
    
    if (assistantId) {
        state.assistantId = assistantId;
        localStorage.setItem('assistantId', assistantId);
    }
    
    closeSettings();
    addMessageToChat({
        role: 'agent',
        content: `✅ Settings saved!\n• Deployment URL: ${deploymentUrl}\n• Assistant ID: ${assistantId}`
    });
}

// Close modals on backdrop click
document.getElementById('settingsModal').addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-backdrop') || e.target.id === 'settingsModal') {
        closeSettings();
    }
});

document.getElementById('fileModal').addEventListener('click', (e) => {
    if (e.target.classList.contains('modal-backdrop') || e.target.id === 'fileModal') {
        closeFileViewer();
    }
});

// Make functions globally available
window.viewFile = viewFile;
window.closeFileViewer = closeFileViewer;
window.copyFileContent = copyFileContent;
window.closeSettings = closeSettings;
window.saveSettings = saveSettings;
