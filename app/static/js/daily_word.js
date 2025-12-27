/**
 * Daily Word module - fetches and displays the daily word from the backend API
 */

async function fetchDailyWord() {
  try {
    const res = await fetch('/daily-word');
    if (!res.ok) {
      throw new Error(`Request failed: ${res.status}`);
    }

    const json = await res.json();
    
    if (json.error || !json.daily_word) {
      throw new Error(json.error || 'No daily word received');
    }

    return {
      word: json.daily_word,
      definition: json.definition || null
    };
  } catch (err) {
    console.error('Failed to fetch daily word:', err);
    return null;
  }
}

async function updateDailyWord() {
  const wordElement = document.getElementById('daily-word');
  const definitionElement = document.getElementById('daily-word-definition');
  
  if (!wordElement) {
    console.error('Daily word element not found');
    return;
  }

  const data = await fetchDailyWord();
  
  if (data && data.word) {
    wordElement.textContent = data.word;
    if (definitionElement) {
      if (data.definition) {
        definitionElement.textContent = data.definition;
      } else {
        definitionElement.textContent = 'Definition unavailable';
      }
    }
  } else {
    wordElement.textContent = 'Word unavailable';
    if (definitionElement) {
      definitionElement.textContent = '--';
    }
  }
}

// Initialize daily word when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', updateDailyWord);
} else {
  updateDailyWord();
}

// Update daily word at midnight
function scheduleDailyWordUpdate() {
  const now = new Date();
  const tomorrow = new Date(now);
  tomorrow.setDate(tomorrow.getDate() + 1);
  tomorrow.setHours(0, 0, 0, 0);
  
  const msUntilMidnight = tomorrow - now;
  
  setTimeout(() => {
    updateDailyWord();
    // Schedule next update
    setInterval(updateDailyWord, 24 * 60 * 60 * 1000); // Update every 24 hours
  }, msUntilMidnight);
}

// Start the daily update scheduler
scheduleDailyWordUpdate();

