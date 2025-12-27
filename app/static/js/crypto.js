// Crypto price fetch and render with rotation

// Populated dynamically from backend `/api/crypto-config`
let COIN_CONFIG = {};
let COIN_IDS = [];
let cryptoData = {};
let currentCoinIndex = 0;
let rotationInterval = null;

// Cache for price data with timestamp
let cachedPriceData = null;
let cachedPriceTimestamp = 0;
const PRICE_CACHE_DURATION_MS = 1000 * 60 * 10; // 10 minutes

async function fetchCryptoPrices() {
  // Check if we have valid cached data
  const now = Date.now();
  if (cachedPriceData && (now - cachedPriceTimestamp) < PRICE_CACHE_DURATION_MS) {
    return cachedPriceData;
  }

  // Fetch fresh data
  const res = await fetch('/api/crypto-price');
  if (!res.ok) throw new Error('Crypto price request failed');
  const json = await res.json();
  if (json.error) {
    throw new Error(json.error);
  }
  
  // Cache the result
  cachedPriceData = json.data || {};
  cachedPriceTimestamp = now;
  
  return cachedPriceData;
}

function formatPrice(price) {
  if (typeof price !== 'number') return '--';
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  }).format(price);
}

function renderCrypto(coinId) {
  const card = document.querySelector('.card-crypto');
  if (!card) return;

  const iconEl = card.querySelector('#crypto-icon');
  const nameEl = card.querySelector('#crypto-name');
  const priceEl = card.querySelector('#crypto-price');
  const indicatorEl = card.querySelector('#crypto-price-indicator');

  const coinConfig = COIN_CONFIG[coinId];
  const priceData = cryptoData[coinId];

  if (!coinConfig || !priceData) {
    if (nameEl) nameEl.textContent = 'Loading...';
    if (priceEl) priceEl.textContent = '--';
    if (indicatorEl) indicatorEl.className = 'crypto-price-indicator';
    return;
  }

  if (iconEl && coinConfig.imageUrl) {
    iconEl.src = coinConfig.imageUrl;
    iconEl.alt = coinConfig.name;
  }

  if (nameEl) {
    nameEl.textContent = coinConfig.name;
  }

  if (priceEl && priceData.usd !== undefined) {
    priceEl.textContent = formatPrice(priceData.usd);
  }

  // Update price indicator based on comparison with yesterday's price
  if (indicatorEl && priceData.usd !== undefined && priceData.usd_yesterday !== undefined) {
    const todayPrice = priceData.usd;
    const yesterdayPrice = priceData.usd_yesterday;
    
    if (todayPrice > yesterdayPrice) {
      // Price increased - green triangle up
      indicatorEl.className = 'crypto-price-indicator crypto-price-up';
      indicatorEl.textContent = '▲';
    } else if (todayPrice < yesterdayPrice) {
      // Price decreased - red triangle down
      indicatorEl.className = 'crypto-price-indicator crypto-price-down';
      indicatorEl.textContent = '▼';
    } else {
      // Price unchanged - no indicator
      indicatorEl.className = 'crypto-price-indicator';
      indicatorEl.textContent = '';
    }
  } else {
    // No yesterday's price available - hide indicator
    indicatorEl.className = 'crypto-price-indicator';
    indicatorEl.textContent = '';
  }
}

function rotateCrypto() {
  if (COIN_IDS.length === 0) return;
  currentCoinIndex = (currentCoinIndex + 1) % COIN_IDS.length;
  const coinId = COIN_IDS[currentCoinIndex];
  renderCrypto(coinId);

  // Notify chart to rotate too
  Events.emit('crypto:rotate', coinId);
}


function initCrypto(Events) {
  const card = document.querySelector('.card-crypto');
  if (!card) return;

  async function loadConfig() {
    // Fetch coin configuration (ids + icons) from backend
    const res = await fetch('/api/crypto-config');
    if (!res.ok) throw new Error('Crypto config request failed');
    const cfg = await res.json();
    COIN_IDS = Array.isArray(cfg.coin_ids) ? cfg.coin_ids : [];
    COIN_CONFIG = cfg.coin_config || {};
    // Expose colors for chart script
    if (typeof window !== 'undefined') {
      window.COIN_COLORS = cfg.coin_colors || {};
    }
    if (COIN_IDS.length === 0) {
      throw new Error('No coin ids configured');
    }
  }

  async function update() {
    try {
      // Ensure config is loaded once
      if (COIN_IDS.length === 0) {
        await loadConfig();
      }
      cryptoData = await fetchCryptoPrices();
      if (Object.keys(cryptoData).length === 0) {
        throw new Error('No crypto data received');
      }

      // Clear existing rotation interval
      if (rotationInterval) {
        clearInterval(rotationInterval);
      }

      // Start with first coin
      currentCoinIndex = 0;
      renderCrypto(COIN_IDS[currentCoinIndex]);

      // Start rotation every 5 seconds
      rotationInterval = setInterval(rotateCrypto, 5000);

      Events.emit('crypto:update', cryptoData);
    } catch (e) {
      // On error, show loading state
      const nameEl = card.querySelector('#crypto-name');
      const priceEl = card.querySelector('#crypto-price');
      if (nameEl) nameEl.textContent = 'Error loading prices';
      if (priceEl) priceEl.textContent = '--';
    }
  }

  update();
  // Refresh data every 10 minutes to reduce API calls
  setInterval(update, 1000 * 60 * 10);
}

