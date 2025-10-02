async function loadDeals() {
  try {
    const res = await fetch('/api/deals');
    const data = await res.json();

    console.log(data); // для проверки в консоли

    const container = document.getElementById('deals');
    container.innerHTML = '';

    data.items.forEach(item => {
      const wrap = document.createElement('div');
      wrap.className = 'tile-wrapper';

      // скидочный бейдж
      const badge = document.createElement('div');
      badge.className = 'discount-badge';
      badge.textContent = item.discount_percent ? `-${item.discount_percent}%` : '';
      wrap.appendChild(badge);

      // плитка
      const tile = document.createElement('div');
      tile.className = 'tile';

      // картинка (с плейсхолдером)
      const img = document.createElement('img');
      img.alt = item.name || 'No Name';
      img.src = item.large_capsule || 'https://store.cloudflare.steamstatic.com/public/images/v6/game_placeholder.png';
      img.addEventListener('click', () => window.open(item.store_link, '_blank'));
      tile.appendChild(img);

      // название игры
      const name = document.createElement('div');
      name.className = 'name';
      name.textContent = item.name || 'No Name';
      tile.appendChild(name);

      // цены
      const prices = document.createElement('div');
      prices.className = 'prices';

      const oldPrice = document.createElement('span');
      oldPrice.className = 'old';
      oldPrice.textContent = (item.initial && item.initial > 0) ? fmt(item.initial, item.currency || 'грн') : '';

      const newPrice = document.createElement('span');
      newPrice.className = 'new';
      newPrice.textContent = (item.final && item.final > 0) ? fmt(item.final, item.currency || 'грн') : 'Free';

      prices.appendChild(oldPrice);
      prices.appendChild(newPrice);
      tile.appendChild(prices);

      wrap.appendChild(tile);
      container.appendChild(wrap);
    });
  } catch (e) {
    console.error('Failed to load deals', e);
  }
}

// функция форматирования цен
function fmt(value, currency = 'грн') {
  if (value === null || value === undefined) return '';
  // если число больше 1000, считаем, что это цена в центах
  if (Number.isInteger(value)) {
    return (value / 100).toFixed(2) + ' ' + currency;
  }
  return value + ' ' + currency;
}

// управление модальным окном About
const aboutBtn = document.getElementById('aboutBtn');
const aboutModal = document.getElementById('aboutModal');
const closeAbout = document.getElementById('closeAbout');

aboutBtn.addEventListener('click', () => aboutModal.setAttribute('aria-hidden', 'false'));
closeAbout.addEventListener('click', () => aboutModal.setAttribute('aria-hidden', 'true'));

// первый рендер
loadDeals();

// автообновление каждые 5 минут
setInterval(loadDeals, 1000 * 60 * 5);
