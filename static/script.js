const messageInput = document.getElementById('messageInput');
const sendButton = document.getElementById('sendButton');
const chatMessages = document.getElementById('chatMessages');
const suggestionButtons = document.querySelectorAll('.chip, .nav-item');

function appendMessage(role, text) {
  const wrapper = document.createElement('div');
  wrapper.className = `message ${role}`;

  const avatar = document.createElement('div');
  avatar.className = 'avatar';
  avatar.textContent = role === 'bot' ? 'V' : 'U';

  const bubble = document.createElement('div');
  bubble.className = 'bubble';

  const label = document.createElement('strong');
  label.textContent = role === 'bot' ? 'VALORANT Coach' : 'Bạn';

  const content = document.createElement('p');
  content.textContent = text;

  bubble.appendChild(label);
  bubble.appendChild(content);

  wrapper.appendChild(avatar);
  wrapper.appendChild(bubble);

  chatMessages.appendChild(wrapper);
  chatMessages.scrollTop = chatMessages.scrollHeight;
}

async function sendMessage(text) {
  const message = text.trim();
  if (!message) return;

  appendMessage('user', message);
  messageInput.value = '';

  const loading = document.createElement('div');
  loading.className = 'message bot';
  loading.innerHTML = `
    <div class="avatar">V</div>
    <div class="bubble">
      <strong>VALORANT Coach</strong>
      <p>Đang phân tích chiến thuật...</p>
    </div>
  `;
  chatMessages.appendChild(loading);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  try {
    const res = await fetch('/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message, user_id: 'web-user' })
    });

    const data = await res.json();

    loading.remove();

    if (!res.ok) {
      appendMessage('bot', data.detail || 'Tôi đang gặp lỗi tạm thời. Hãy thử lại sau.');
      return;
    }

    appendMessage('bot', data.answer || 'Tôi chưa có câu trả lời phù hợp cho bạn.');
  } catch (error) {
    loading.remove();
    appendMessage('bot', 'Máy chủ đang gặp sự cố. Vui lòng thử lại sau ít phút.');
  }
}

sendButton.addEventListener('click', () => sendMessage(messageInput.value));
messageInput.addEventListener('keydown', (event) => {
  if (event.key === 'Enter') {
    sendMessage(messageInput.value);
  }
});

suggestionButtons.forEach((button) => {
  button.addEventListener('click', () => {
    const prompt = button.getAttribute('data-prompt');
    if (prompt) {
      messageInput.value = prompt;
      sendMessage(prompt);
    }
  });
});
