// Weather fetch and render

async function fetchWeather(cityKey) {
  const endpoint = cityKey === 'second-city' ? '/api/weather/second-city' : '/api/weather/first-city';
  const res = await fetch(endpoint);
  if (!res.ok) throw new Error('Weather request failed');
  return res.json();
}

function renderWeather(rootEl, data) {
  const tempEl = rootEl.querySelector('#weather-temp');
  const cityEl = rootEl.querySelector('#weather-city');
  const iconEl = rootEl.querySelector('#weather-icon');
  const sunriseEl = rootEl.querySelector('#weather-sunrise');
  const sunsetEl = rootEl.querySelector('#weather-sunset');
  const windSpeedEl = rootEl.querySelector('#weather-wind-speed');
  const rainPrecipitationEl = rootEl.querySelector('#weather-rain-precipitation');
  const feelsLikeEl = rootEl.querySelector('#weather-feels-like');

  if (tempEl && typeof data.temp === 'number') tempEl.textContent = `${Math.round(data.temp)}°`;
  if (cityEl) cityEl.textContent = data.city ? data.city.toString() : '';
  if (iconEl) iconEl.src = iconSrc(data.icon);
  const timeFmt = { hour: '2-digit', minute: '2-digit' };
  if (sunriseEl) sunriseEl.textContent = data.sunrise ? new Date(data.sunrise * 1000).toLocaleTimeString(undefined, timeFmt) : '';
  if (sunsetEl) sunsetEl.textContent = data.sunset ? new Date(data.sunset * 1000).toLocaleTimeString(undefined, timeFmt) : '';
  if (windSpeedEl) {
    const speed = data.wind_speed;
    if (typeof speed === 'number') {
      const unit = data.units === 'metric' ? 'm/s' : 'mph';
      windSpeedEl.textContent = `${speed.toFixed(1)} ${unit}`;
    } else {
      windSpeedEl.textContent = '--';
    }
  }
  if (rainPrecipitationEl) {
    const rain = data.rain_precipitation;
    if (typeof rain === 'number') {
      rainPrecipitationEl.textContent = `${rain.toFixed(1)} mm`;
    }
    if (rain === null) {
      rainPrecipitationEl.textContent = '0 mm';
    } else {
      rainPrecipitationEl.textContent = `${rain.toFixed(1)} mm`;
    }
  }
  if (feelsLikeEl) {
    const feelsLike = data.feels_like;
    if (typeof feelsLike === 'number') {
      feelsLikeEl.textContent = `Feels like ${Math.round(feelsLike)}°`;
    } else {
      feelsLikeEl.textContent = 'Feels like --°';
    }
  }
}

function initWeather(Events) {
  const cards = Array.from(document.querySelectorAll('.card-weather'));
  cards.forEach((card, index) => {
    const cityKey = index === 1 ? 'second-city' : 'first-city';

    async function update() {
      try {
        const data = await fetchWeather(cityKey);
        renderWeather(card, data);
        Events.emit(`weather:update:${cityKey}`, data);
      } catch (e) {
        // ignore
      }

      try {
        const forecastEndpoint = cityKey === 'second-city' ? '/api/forecast/second-city' : '/api/forecast/first-city';
        const forecastRes = await fetch(forecastEndpoint);
        if (forecastRes.ok) {
          const forecast = await forecastRes.json();
          renderForecast(card, forecast);
          Events.emit(`weather:forecast:${cityKey}`, forecast);
        }
      } catch (e) {
        // ignore
      }
    }

    update();
    setInterval(update, 1000 * 60 * 15);
  });
}

function unixToWeekday(unixSeconds, offsetSeconds = 0) {
  if (!unixSeconds) return '';
  const d = new Date((unixSeconds + offsetSeconds) * 1000);
  return d.toLocaleDateString(undefined, { weekday: 'short' });
}

function renderForecast(rootEl, payload) {
  const forecastItems = Array.from(rootEl.querySelectorAll('.forecast-item'));
  if (!forecastItems.length) return;
  const items = Array.isArray(payload?.items) ? payload.items.slice(0, 3) : [];

  forecastItems.forEach((item, index) => {
    const it = items[index];
    const icon = item.querySelector('.forecast-icon');
    const day = item.querySelector('.forecast-day');
    const desc = item.querySelector('.forecast-desc');
    const minmax = item.querySelector('.forecast-minmax');

    if (!it) {
      if (icon) icon.src = '';
      if (day) day.textContent = '--';
      if (desc) desc.textContent = '--';
      if (minmax) minmax.textContent = '--° / --°';
      return;
    }

    if (icon) icon.src = iconSrc(it.icon);
    if (day) day.textContent = unixToWeekday(it.dt);
    if (desc) desc.textContent = it.description || '';
    if (minmax) {
      const minTxt = typeof it.temp_min === 'number' ? `${Math.round(it.temp_min)}°` : '--°';
      const maxTxt = typeof it.temp_max === 'number' ? `${Math.round(it.temp_max)}°` : '--°';
      minmax.textContent = `${maxTxt} / ${minTxt}`;
    }
  });
}


function iconSrc(code) {
  if (code === '01d') {
    return '/static/assets/icons/weather/day-clear.svg';
  }
  if (code === '01n') {
    return '/static/assets/icons/weather/night-clear.svg';
  }
  if (code === '02d') {
    return '/static/assets/icons/weather/day-few-clouds.svg';
  }
  if (code === '02n') {
    return '/static/assets/icons/weather/night-few-clouds.svg';
  }
  if (code === '10d') {
    return '/static/assets/icons/weather/day-rain.svg';
  }
  if (code === '10n') {
    return '/static/assets/icons/weather/night-rain.svg';
  }
  if (code == '03d' || code == '03n') {
    return '/static/assets/icons/weather/scattered-clouds.svg';
  }
  if (code == '04d' || code == '04n') {
    return '/static/assets/icons/weather/broken-clouds.svg';
  }
  if (code == '09d' || code == '09n') {
    return '/static/assets/icons/weather/shower-rain.svg';
  }
  if (code == '13d' || code == '13n') {
    return '/static/assets/icons/weather/snow.svg';
  }
  if (code == '50d' || code == '50n') {
    return '/static/assets/icons/weather/mist.svg';
  }
  return `https://openweathermap.org/img/wn/${code || '01d'}@2x.png`;
}


