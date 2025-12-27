// Clock and date rendering

function formatTime(date) {
  const h = date.getHours().toString().padStart(2, '0');
  const m = date.getMinutes().toString().padStart(2, '0');
  return `${h}:${m}`;
}

function formatDate(date) {
  return date.toLocaleDateString(undefined, {
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric'
  });
}

function initClock(Events) {
  const timeEl = document.getElementById('clock-time');
  const dateEl = document.getElementById('clock-date');

  function tick() {
    const now = new Date();
    if (timeEl) timeEl.textContent = formatTime(now);
    if (dateEl) dateEl.textContent = formatDate(now);
    Events.emit('time:tick', now);
  }

  tick();
  setInterval(tick, 1000 * 30); // update every 30s (sufficient for minutes display)
}


