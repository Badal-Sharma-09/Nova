document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('chat-form');
    const messageInput = document.getElementById('message');
    const chatMessages = document.getElementById('chat-messages');
    const errorModal = document.getElementById('error-modal');
    const closeModal = document.getElementById('close-modal');
    let currentChatId = null;
    const chatHistory = document.getElementById('chat-history');
    const chatTitle = document.getElementById('chat-title');
    const newChatBtn = document.getElementById('new-chat-btn');
    const renameModal = document.getElementById('rename-modal');
    const deleteModal = document.getElementById('delete-modal');
    const newTitleInput = document.getElementById('new-title');

    // Auto-resize textarea
    messageInput.addEventListener('input', function () {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });

    // Close modal when clicking the close button
    closeModal.addEventListener('click', function () {
        errorModal.classList.add('hidden');
    });

    // Function to show error modal
    function showErrorModal() {
        errorModal.classList.remove('hidden');
    }

    function formatDateHeader(dateStr) {
        const now = new Date();
        const date = new Date(dateStr);
        const diffTime = now - date;
        const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));

        if (diffDays === 0) return "Today";
        if (diffDays === 1) return "Yesterday";

        // If same month
        if (now.getMonth() === date.getMonth() && now.getFullYear() === date.getFullYear()) {
            return "This Month";
        }

        // Default to full month
        return date.toLocaleString('default', { month: 'long', year: 'numeric' });
    }

    // Add message to chat 
  function addMessageToChat(sender, message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = sender === 'user'
        ? 'flex justify-end items-start mb-4'
        : 'flex items-start space-x-3 mb-4';

    const avatarDiv = document.createElement('div');
    avatarDiv.className = sender === 'user' ? 'flex-shrink-0 ml-3' : 'flex-shrink-0';

    const avatar = document.createElement('div');
    avatar.className = sender === 'user'
        ? 'h-8 w-8 rounded-full bg-green-500 flex items-center justify-center text-white font-semibold'
        : 'h-10 w-10 rounded-full bg-blue-500 flex items-center justify-center text-white font-semibold';

    const avatarText = document.createElement('span');
    avatarText.textContent = sender === 'user' ? 'You' : 'AI';
    avatarText.className = 'text-sm font-medium';
    avatar.appendChild(avatarText);
    avatarDiv.appendChild(avatar);

    const messageContent = document.createElement('div');
    messageContent.className = 'max-w-[75%]';

    // Message bubble
    const messageBubble = document.createElement('div');
    messageBubble.className = sender === 'user'
        ? 'bg-blue-100 text-gray-900 px-4 py-3 rounded-2xl'
        : 'bg-gray-100 text-gray-800 px-4 py-3 rounded-2xl';

    const messageText = document.createElement('p');
    messageText.className = 'text-gray-700';
    messageText.textContent = message;
    messageBubble.appendChild(messageText);
    messageContent.appendChild(messageBubble);

    // Button actions (AI: like/dislike/copy/redo | User: edit)
    const actionRow = document.createElement('div');
    actionRow.className = 'flex items-center space-x-3 mt-1 text-sm text-gray-500';

    if (sender === 'ai') {
        actionRow.innerHTML = `
             <button class="like-btn hover:text-blue-600" onclick="sendFeedback(this, 'like')">
            <img src="{{ url_for('static', filename='images/like.png') }}" alt="Like"
             class="h-6 w-6 object-cover"
             onerror="this.style.display='none';" />
            </button>
            <button class="dislike-btn hover:text-red-600" onclick="sendFeedback(this, 'dislike')">👎</button>
            <button class="copy-btn hover:text-green-600" onclick="copyToClipboard(this)">📋</button>
            <button class="redo-btn hover:text-purple-600" onclick="regenerateResponse(this)">🔄</button>
        `;
    } else {
        actionRow.innerHTML = `
            <button class="edit-btn hover:text-blue-600" onclick="editMessage(this)">✏️ Edit</button>
        `;
    }

    messageContent.appendChild(actionRow);

    if (sender === 'user') {
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(avatarDiv);
    } else {
        messageDiv.appendChild(avatarDiv);
        messageDiv.appendChild(messageContent);
    }

    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

    // Load chat history
    async function loadChatHistory() {
        try {
            const response = await fetch('/get_chat_history');
            const data = await response.json();

            chatHistory.innerHTML = '';
            let grouped = {};

            data.chats.forEach(chat => {
                const groupKey = formatDateHeader(chat.last_interaction || chat.timestamp);

                if (!grouped[groupKey]) {
                    grouped[groupKey] = [];
                }

                grouped[groupKey].push(chat);
            });

            Object.keys(grouped).forEach(group => {
                // Group header
                const groupHeader = document.createElement('div');
                groupHeader.className = 'text-xs font-bold text-gray-500 uppercase px-3 pt-4 pb-1';
                groupHeader.textContent = group;
                chatHistory.appendChild(groupHeader);

                // Grouped chats
                grouped[group].forEach(chat => {
                    const chatItem = document.createElement('div');
                    chatItem.className = `p-3 rounded-lg cursor-pointer hover:bg-gray-200 ${currentChatId === chat._id ? 'bg-gray-300' : ''}`;
                    chatItem.innerHTML = `
                           <div class="text-sm font-medium truncate">${chat.title}</div>
                           <div class="text-xs text-gray-400">${new Date(chat.last_interaction || chat.timestamp).toLocaleString()}</div>
                            `;
                    chatItem.onclick = () => loadChat(chat._id);
                    chatHistory.appendChild(chatItem);
                });
            });
        } catch (error) {
            console.error('Error loading chat history:', error);
        }
    }

    // Load specific chat
    async function loadChat(chatId) {
        try {
            const response = await fetch(`/get_chat_messages/${chatId}`);
            const data = await response.json();

            currentChatId = chatId;
            chatTitle.textContent = data.title;
            chatMessages.innerHTML = '';

            // Add welcome message
            addMessageToChat('ai', 'Hello! I\'m your AI assistant. How can I help you today?');

            // Add chat history
            if (data.history && Array.isArray(data.history)) {
                data.history.forEach(msg => {
                    addMessageToChat(msg.role === 'user' ? 'user' : 'ai', msg.parts[0]);
                });
            }

            loadChatHistory(); // Refresh sidebar
        } catch (error) {
            console.error('Error loading chat:', error);
        }
    }

    // Create new chat
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    async function createNewChat() {
        try {
            const response = await fetch('/create_chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });

            if (!response.ok) {
                throw new Error('Failed to create new chat');
            }

            const data = await response.json();

            // Update state and UI
            currentChatId = data.chat_id;

            // Clear messages and title
            chatTitle.textContent = data.title || "New Chat";
            chatMessages.innerHTML = '';

            // Add welcome message
            addMessageToChat('ai', "Hello! I'm your AI assistant. How can I help you today?");

            // Load the chat into sidebar & history
            await loadChatHistory();
            await loadChat(currentChatId);  // Important to update messages panel!

        } catch (error) {
            console.error('Error creating new chat:', error);
            showErrorModal?.();
        }
    }

    // Delete chat
    async function deleteChat() {
        if (!currentChatId) return;

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const response = await fetch(`/delete_chat/${currentChatId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
            });

            if (response.ok) {
                // Get updated chat history
                const historyResponse = await fetch('/get_chat_history');
                const historyData = await historyResponse.json();

                if (historyData.chats && historyData.chats.length > 0) {
                    // Load the most recent chat
                    await loadChat(historyData.chats[0]._id);
                } else {
                    // If no chats exist, then create a new one
                    await createNewChat();
                }
            }
        } catch (error) {
            console.error('Error deleting chat:', error);
            addMessageToChat('ai', 'Sorry, I encountered an error while deleting the chat. Please try again.');
        }
    }

    // Rename chat
    async function renameChat(newTitle) {
        if (!currentChatId) return;

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const response = await fetch(`/update_chat_title/${currentChatId}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ title: newTitle })
            });

            if (response.ok) {
                chatTitle.textContent = newTitle;
                loadChatHistory(); // Refresh sidebar
            }
        } catch (error) {
            console.error('Error renaming chat:', error);
        }
    }

    // Ensure no double event binding
    if (!newChatBtn.dataset.bound) {
        newChatBtn.addEventListener("click", () => {
            if (initializing) return;
            createNewChat();
        });
        newChatBtn.dataset.bound = "true"; // mark as bound
    }

    document.getElementById('rename-chat').addEventListener('click', () => {
        if (!currentChatId) return;
        newTitleInput.value = chatTitle.textContent;
        renameModal.classList.remove('hidden');
    });

    document.getElementById('delete-chat').addEventListener('click', () => {
        if (!currentChatId) return;
        deleteModal.classList.remove('hidden');
    });

    document.getElementById('confirm-rename').addEventListener('click', () => {
        const newTitle = newTitleInput.value.trim();
        if (newTitle) {
            renameChat(newTitle);
            renameModal.classList.add('hidden');
        }
    });

    document.getElementById('cancel-rename').addEventListener('click', () => {
        renameModal.classList.add('hidden');
    });

    document.getElementById('confirm-delete').addEventListener('click', () => {
        deleteChat();
        deleteModal.classList.add('hidden');
    });

    document.getElementById('cancel-delete').addEventListener('click', () => {
        deleteModal.classList.add('hidden');
    });

    // Close modals when clicking outside
    window.addEventListener('click', (event) => {
        if (event.target === renameModal) {
            renameModal.classList.add('hidden');
        }
        if (event.target === deleteModal) {
            deleteModal.classList.add('hidden');
        }
    });

    // Chat form submission
    chatForm.addEventListener('submit', async function (e) {
        e.preventDefault();
        const message = messageInput.value.trim();
        console.log("User input:", messageInput.value);
        console.log("Trimmed message:", message);
        if (!message) {
            // alert("Please type a message.");
            return;
        }

        // Clear input and reset height
        messageInput.value = '';
        messageInput.style.height = 'auto';

        // Add user message to chat
        addMessageToChat('user', message);

        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    message: message,
                    chat_id: currentChatId
                })
            });

            const data = await response.json();

            if (!response.ok) {
                const data = await response.json();
                console.error("API Error:", data.error); // ← Add this

                if (data.error && (data.error.includes('quota') || data.error.includes('429'))) {
                    showErrorModal();
                    return;
                }

                throw new Error(data.error || 'Network response was not ok');
            }

            // Update current chat ID and add AI response
            currentChatId = data.chat_id;
            addMessageToChat('ai', data.response);

            // Refresh chat history
            loadChatHistory();
        } catch (error) {
            console.error('❌ Chat API failed:', error);

            try {
                const text = await response.text();
                console.error('Raw response:', text);
            } catch (e) {
                console.error('Could not parse error response:', e);
            }

            // existing fallback
            if (error.message && (error.message.includes('quota') || error.message.includes('429'))) {
                addMessageToChat('ai', '⚠️ You’re sending messages too quickly. Please wait a few seconds.');

                const toast = document.getElementById('toast-warning');
                toast.style.display = 'block';

                messageInput.disabled = true;
                messageInput.classList.add('bg-gray-100', 'cursor-not-allowed');

                setTimeout(() => {
                    toast.style.display = 'none';
                    messageInput.disabled = false;
                    messageInput.classList.remove('bg-gray-100', 'cursor-not-allowed');
                }, 5000);  // re-enable after 5 seconds

                showErrorModal?.();
            } else {
                addMessageToChat('ai', '😕 Sorry, I encountered an error. Please try again.');
            }
        }
    });


    let initializing = true;

    (async function initializeChat() {
        const response = await fetch('/get_chat_history');
        const data = await response.json();

        if (data.chats && data.chats.length > 0) {
            await loadChat(data.chats[0]._id);
        } else {
            console.log("📦 Initializing empty chat...");
            await createNewChat(); // only if no chat
        }

        initializing = false;
    })();
});
