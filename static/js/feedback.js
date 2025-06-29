// feedback.js
document.addEventListener('DOMContentLoaded', function () { 

    // Show Emoji Overlay
    function showEmojiOverlay(button, emoji) {
        if (button.querySelector('.emoji-overlay')) return;

        const overlay = document.createElement("span");
        overlay.className = "emoji-overlay absolute top-0 left-0 w-full h-full flex items-center justify-center text-xl bg-white/70 rounded";
        overlay.textContent = emoji;

        button.style.position = 'relative';
        button.appendChild(overlay);

        setTimeout(() => overlay.remove(), 1000);
    }

    // Copy to Clipboard
    function copyToClipboard(button) {
        const message = button.closest('.flex')?.previousElementSibling?.innerText;
        if (message) {
            navigator.clipboard.writeText(message).then(() => {
                showEmojiOverlay(button, "✅");
            });
        }
    }

    // Send Feedback (Like / Dislike)
    function sendFeedback(button, type) {
        const tooltip = button.querySelector('.tooltip') || createTooltip(button);

        if (type === 'like') {
            button.classList.add('text-blue-600');
            tooltip.textContent = 'Good response';
            showEmojiOverlay(button, "👍");
        } else if (type === 'dislike') {
            button.classList.add('text-red-600');
            tooltip.textContent = 'We’ll use this to improve';
            showEmojiOverlay(button, "👎");
        }

        tooltip.style.opacity = '1';
        setTimeout(() => tooltip.style.opacity = '0', 1500);

        button.disabled = true;
        button.classList.add('cursor-not-allowed');
    }

    // Regenerate AI Response
    function regenerateResponse(button) {
        const container = button.closest('.tooltip-container')?.closest('div');
        const messageEl = container?.querySelector('p');

        if (!messageEl || !messageEl.innerText) {
            console.warn("⚠️ No message text found for regeneration.");
            return;
        }

        const messageText = messageEl.innerText;

        fetch('/regenerate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message: messageText })
        })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Regeneration failed');
                }
                return response.json();
            })
            .then(data => {
                const newResponse = document.createElement('p');
                newResponse.className = "bg-slate-100 px-4 py-2 rounded-xl text-gray-800";
                newResponse.innerText = data.new_response;
                container.insertBefore(newResponse, container.querySelector('.flex') || null);
            })
            .catch(err => {
                console.error('❌ Error regenerating response:', err);
            });
    }

    // Edit Message
    function editMessage(button) {
        const wrapper = button.closest('div');
        const msgBlock = wrapper.previousElementSibling;
        const originalText = msgBlock.innerText;

        const textarea = document.createElement("textarea");
        textarea.className = "w-full rounded-md border px-3 py-2 text-gray-700";
        textarea.value = originalText;

        msgBlock.replaceWith(textarea);

        const saveBtn = document.createElement("button");
        saveBtn.textContent = "💾 Save";
        saveBtn.className = "text-green-600 hover:text-green-800 mr-2";
        saveBtn.onclick = () => {
            const newText = textarea.value;
            const newP = document.createElement("p");
            newP.className = "bg-blue-100 text-blue-900 px-4 py-2 rounded-xl editable";
            newP.innerText = newText;
            textarea.replaceWith(newP);
            saveBtn.remove();
            cancelBtn.remove();
            button.style.display = 'inline';
        };

        const cancelBtn = document.createElement("button");
        cancelBtn.textContent = "❌ Cancel";
        cancelBtn.className = "text-red-600 hover:text-red-800";
        cancelBtn.onclick = () => {
            textarea.replaceWith(msgBlock);
            saveBtn.remove();
            cancelBtn.remove();
            button.style.display = 'inline';
        };

        wrapper.appendChild(saveBtn);
        wrapper.appendChild(cancelBtn);
        button.style.display = 'none';
    }

    // Create Tooltip
    function createTooltip(button) {
        const tooltip = document.createElement('span');
        tooltip.className = 'tooltip absolute top-[-30px] bg-black text-white text-xs px-2 py-1 rounded';
        tooltip.style.transition = 'opacity 0.3s';
        tooltip.style.opacity = '0';
        button.appendChild(tooltip);
        return tooltip;
    }

    // Make functions global so onclick works in HTML
    window.copyToClipboard = copyToClipboard;
    window.sendFeedback = sendFeedback;
    window.regenerateResponse = regenerateResponse;
    window.editMessage = editMessage;

});
