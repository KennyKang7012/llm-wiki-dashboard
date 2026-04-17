const healthEl = document.getElementById('health');
const questionEl = document.getElementById('question');
const answerEl = document.getElementById('answer');
const sourcesEl = document.getElementById('sources');
const askBtn = document.getElementById('askBtn');

async function loadHealth() {
  try {
    const res = await fetch('/api/health');
    const data = await res.json();
    healthEl.textContent = `模式：${data.mode} | 文件數：${data.docs} | 模型：${data.model}`;
  } catch {
    healthEl.textContent = '無法連線後端';
  }
}

function renderSources(sources) {
  sourcesEl.innerHTML = '';
  if (!sources || sources.length === 0) {
    sourcesEl.innerHTML = '<li>無</li>';
    return;
  }

  for (const src of sources) {
    const li = document.createElement('li');
    li.textContent = `${src.title} (${src.path})`;
    sourcesEl.appendChild(li);
  }
}

async function askQuestion() {
  const question = questionEl.value.trim();
  if (!question) {
    answerEl.textContent = '請先輸入問題。';
    return;
  }

  askBtn.disabled = true;
  askBtn.textContent = '處理中...';
  answerEl.textContent = '正在分析...';

  try {
    const res = await fetch('/api/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question }),
    });
    const data = await res.json();

    if (!res.ok) {
      answerEl.textContent = data.error || '發生錯誤';
      renderSources([]);
      return;
    }

    const warning = data.warning ? `\n\n[警告] ${data.warning}` : '';
    answerEl.textContent = (data.answer || '無回答') + warning;
    renderSources(data.sources || []);
  } catch (err) {
    answerEl.textContent = `請求失敗：${err}`;
    renderSources([]);
  } finally {
    askBtn.disabled = false;
    askBtn.textContent = '送出問題';
    loadHealth();
  }
}

askBtn.addEventListener('click', askQuestion);
questionEl.addEventListener('keydown', (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    askQuestion();
  }
});

loadHealth();
