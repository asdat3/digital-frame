// Main initialization and simple pub/sub

const Events = {
  _events: {},
  on(event, fn) {
    (this._events[event] = this._events[event] || []).push(fn);
  },
  emit(event, ...args) {
    (this._events[event] || []).forEach(fn => fn(...args));
  }
};

function init() {
  initClock(Events);
  initWeather(Events);
  if (typeof initCalendar === 'function') initCalendar(Events);
  if (typeof initCrypto === 'function') initCrypto(Events);
  if (typeof initCryptoChart === 'function') initCryptoChart(Events);
}

window.addEventListener('DOMContentLoaded', init);


