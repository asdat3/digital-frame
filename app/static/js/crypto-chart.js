// Colors are now provided by backend and exposed on window.COIN_COLORS
let COIN_COLORS = (typeof window !== 'undefined' && window.COIN_COLORS) ? window.COIN_COLORS : {};

let chartInstance = null;
let currentChartCoinId = null;

// Cache for historical data with timestamps
let cachedChartData = {};
const CHART_CACHE_DURATION_MS = 1000 * 60 * 10; // 10 minutes

async function loadChart(coinId) {
  const canvas = document.getElementById("crypto-chart");
  if (!canvas) return console.error("Canvas #crypto-chart not found");

  // Skip if already showing this coin
  if (chartInstance && currentChartCoinId === coinId) {
    return;
  }

  if (chartInstance) {
    chartInstance.destroy();
    chartInstance = null;
  }

  try {
    let json;
    const now = Date.now();
    
    // Check if we have valid cached data for this coin
    if (cachedChartData[coinId] && (now - cachedChartData[coinId].timestamp) < CHART_CACHE_DURATION_MS) {
      json = cachedChartData[coinId].data;
    } else {
      // Fetch fresh data
      const res = await fetch(`/api/crypto-history/${coinId}`);
      if (!res.ok) throw new Error(res.statusText);
      json = await res.json();
      
      // Cache the result
      cachedChartData[coinId] = {
        data: json,
        timestamp: now
      };
    }
    
    if (json.error || !json.prices?.length) throw new Error("No price data");

    const prices = json.prices.map(p => ({ date: new Date(p[0]), price: p[1] }));
    const labels = prices.map(p =>
      p.date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
    );
    const dataPoints = prices.map(p => p.price);

    const fallback = { border: "rgba(255, 140, 0, 0.8)", background: "rgba(247, 147, 26, 0.1)" };
    const colors = (COIN_COLORS && COIN_COLORS[coinId]) || (COIN_COLORS && COIN_COLORS.bitcoin) || fallback;
    const dataMin = Math.min(...dataPoints);
    const dataMax = Math.max(...dataPoints);
    const tol = Math.abs(dataMax - dataMin) * 0.001;

    chartInstance = new Chart(canvas, {
      type: "line",
      data: {
        labels,
        datasets: [{
          data: dataPoints,
          borderColor: colors.border,
          backgroundColor: colors.background,
          tension: 0.3,
          pointRadius: 0,
          pointHoverRadius: 0
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        animation: false,
        transitions: {
          active: {
            animation: { duration: 0 }
          }
        },
        layout: { padding: { top: 8, bottom: 8 } },
        plugins: { 
          legend: { display: false },
          tooltip: { enabled: false }
        },
        interaction: {
          intersect: false,
          mode: 'nearest'
        },
        scales: {
          x: {
            grid: { display: false },
            ticks: { display: false }
          },
          y: {
            beginAtZero: false,
            includeBounds: true,
            min: dataMin,
            max: dataMax,
            afterDataLimits(scale) {
              scale.min = dataMin;
              scale.max = dataMax;
            },
            grid: { color: "rgba(255,255,255,0.1)" },
            ticks: {
              color: "#ffffff",
              font: { weight: 'bold' },
              count: 2,
              callback(value) {
                const isMin = Math.abs(value - dataMin) < tol;
                const isMax = Math.abs(value - dataMax) < tol;
                if (isMin || isMax) {
                  return '$' + Math.round(value).toLocaleString();
                }
                return '';
              }
            }
          }
        }
      }
    });

    currentChartCoinId = coinId;

  } catch (err) {
    console.error(`Chart load failed for ${coinId}:`, err);
    currentChartCoinId = null;
  }
}

function initCryptoChart(Events) {
  if (typeof Chart === 'undefined')
    return setTimeout(() => initCryptoChart(Events), 100);
  const canvas = document.getElementById("crypto-chart");
  if (!canvas)
    return setTimeout(() => initCryptoChart(Events), 200);
  if (typeof COIN_IDS === 'undefined' || !Array.isArray(COIN_IDS) || COIN_IDS.length === 0)
    return setTimeout(() => initCryptoChart(Events), 200);
  if (!COIN_COLORS || Object.keys(COIN_COLORS).length === 0) {
    // Try to pick up colors assigned later by crypto.js
    if (typeof window !== 'undefined' && window.COIN_COLORS) {
      COIN_COLORS = window.COIN_COLORS;
    } else {
      return setTimeout(() => initCryptoChart(Events), 200);
    }
  }

  loadChart(COIN_IDS[0]);

  Events.on('crypto:rotate', coinId => loadChart(coinId));
  Events.on('crypto:update', () => {
    const coin = COIN_IDS?.[currentCoinIndex];
    if (coin) loadChart(coin);
  });
}
