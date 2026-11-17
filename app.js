const $ = (id) => document.getElementById(id);
let currentMorse = '';
let currentText = '';
let toastTimer;

function toast(message) {
  const box = $('toast'); box.textContent = message; box.classList.add('show');
  clearTimeout(toastTimer); toastTimer = setTimeout(() => box.classList.remove('show'), 3200);
}
async function api(url, options = {}) {
  const response = await fetch(url, {headers: {'Content-Type': 'application/json'}, ...options});
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Ocurrió un error.');
  return data;
}

$('encodeBtn').addEventListener('click', async () => {
  try {
    const data = await api('/api/encode', {method:'POST', body:JSON.stringify({text:$('textInput').value})});
    currentMorse = data.morse; currentText = data.text;
    $('encodeOutput').textContent = data.morse; toast('Mensaje convertido a código Morse.'); loadHistory();
  } catch (e) { toast(e.message); }
});

$('decodeBtn').addEventListener('click', async () => {
  try {
    const data = await api('/api/decode', {method:'POST', body:JSON.stringify({morse:$('morseInput').value})});
    currentMorse = data.morse; currentText = data.text;
    $('decodeOutput').textContent = data.text; toast('Código Morse traducido.'); loadHistory();
  } catch (e) { toast(e.message); }
});

$('playBtn').addEventListener('click', async () => {
  if (!currentMorse) { toast('Primero convierte un mensaje a Morse.'); return; }
  try { const data = await api('/api/play', {method:'POST', body:JSON.stringify({morse:currentMorse})}); toast(data.message); }
  catch (e) { toast(e.message); }
});

document.querySelectorAll('[data-symbol]').forEach(button => button.addEventListener('click', () => {
  const input = $('morseInput'); input.value += button.dataset.symbol; input.focus();
}));

document.querySelectorAll('[data-copy]').forEach(button => button.addEventListener('click', async () => {
  const text = $(button.dataset.copy).textContent;
  try { await navigator.clipboard.writeText(text); toast('Texto copiado.'); }
  catch { toast('No fue posible copiar automáticamente.'); }
}));

async function readButton() {
  try {
    const data = await api('/api/button');
    if (data.morse) {
      $('buttonMorse').textContent = data.morse;
      $('buttonText').textContent = data.text || 'Señal recibida.';
      $('buttonStatus').textContent = 'Señal recibida correctamente.';
      $('ledIndicator').classList.add('active'); setTimeout(()=>$('ledIndicator').classList.remove('active'),700);
      loadHistory();
    } else $('buttonStatus').textContent = 'No hay señales nuevas.';
  } catch (e) { toast(e.message); }
}
$('readButton').addEventListener('click', readButton);

async function loadHistory() {
  try {
    const data = await api('/api/history'); const list = $('historyList');
    if (!data.messages.length) { list.innerHTML = '<p class="empty-state">Todavía no hay mensajes guardados.</p>'; return; }
    list.replaceChildren();
    data.messages.forEach(item => {
      const row = document.createElement('div'); row.className = 'history-item';
      const text = document.createElement('div'); text.className = 'history-text'; text.textContent = item.texto;
      const code = document.createElement('div'); code.className = 'history-code'; code.textContent = item.codigo_morse;
      const meta = document.createElement('div'); meta.className = 'history-meta'; meta.textContent = `${item.direccion.replaceAll('_',' ')} · ${item.fecha_hora}`;
      row.append(text, code, meta); list.append(row);
    });
  } catch (e) { console.error(e); }
}
$('clearHistory').addEventListener('click', async () => {
  if (!confirm('¿Seguro que deseas borrar todo el historial?')) return;
  try { await api('/api/history', {method:'DELETE'}); loadHistory(); toast('Historial eliminado.'); }
  catch (e) { toast(e.message); }
});
$('sendRemote').addEventListener('click', async () => {
  if (!currentMorse || !currentText) { toast('Primero convierte un mensaje en Texto a Morse.'); return; }
  try {
    const data = await api('/api/inbox', {method:'POST', body:JSON.stringify({sender:$('senderName').value || 'Visitante', text:currentText, morse:currentMorse})});
    toast(data.message); loadHistory(); loadInbox();
  } catch (e) { toast(e.message); }
});

async function loadInbox() {
  try {
    const data = await api('/api/inbox');
    const list = $('inboxList');
    $('inboxStatus').textContent = 'Actualización automática cada 3 segundos';
    if (!data.messages.length) { list.innerHTML = '<p class="empty-state">Todavía no hay mensajes. ¡Envía el primero!</p>'; return; }
    list.replaceChildren();
    data.messages.slice(0,30).forEach(item => {
      const card = document.createElement('article'); card.className = 'inbox-message';
      const heading = document.createElement('strong'); heading.textContent = item.texto;
      const morse = document.createElement('div'); morse.className = 'history-code'; morse.textContent = item.codigo_morse;
      const meta = document.createElement('small'); meta.textContent = `${item.fecha_hora} · ${item.medio || 'Internet'}`;
      card.append(heading, morse, meta); list.append(card);
    });
  } catch (e) { $('inboxStatus').textContent = 'Sin conexión; reintentando...'; }
}

loadHistory();
loadInbox();
setInterval(loadInbox, 3000);
