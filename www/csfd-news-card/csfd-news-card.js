class CSFDNewsCard extends HTMLElement {
  set hass(hass) {
    if (!this._initialized) {
      this._initialized = true;
      const card = document.createElement('ha-card');
      card.header = this.config.title || 'ČSFD Novinky';
      this.appendChild(card);

      const style = document.createElement('style');
      style.textContent = `
        .csfd-news-container {
          padding: 16px;
          max-height: 600px;
          overflow-y: auto;
          overflow-x: hidden;
        }
        .csfd-news-container::-webkit-scrollbar {
          width: 8px;
        }
        .csfd-news-container::-webkit-scrollbar-track {
          background: var(--primary-background-color);
        }
        .csfd-news-container::-webkit-scrollbar-thumb {
          background: var(--secondary-text-color);
          border-radius: 4px;
        }
        .csfd-news-container::-webkit-scrollbar-thumb:hover {
          background: var(--primary-text-color);
        }
        .news-item {
          display: flex;
          margin-bottom: 16px;
          padding: 12px;
          border-radius: 8px;
          background: var(--primary-background-color);
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
          transition: transform 0.2s, box-shadow 0.2s;
          cursor: pointer;
        }
        .news-item:last-child {
          margin-bottom: 0;
        }
        .news-item:hover {
          transform: translateY(-2px);
          box-shadow: 0 4px 8px rgba(0,0,0,0.2);
        }
        .news-image {
          width: 120px;
          height: 80px;
          object-fit: cover;
          border-radius: 4px;
          margin-right: 12px;
          flex-shrink: 0;
        }
        .news-content {
          flex: 1;
          display: flex;
          flex-direction: column;
          min-width: 0;
        }
        .news-title {
          font-weight: bold;
          font-size: 14px;
          margin-bottom: 4px;
          color: var(--primary-text-color);
          line-height: 1.3;
        }
        .news-date {
          font-size: 12px;
          color: var(--secondary-text-color);
          margin-bottom: 6px;
        }
        .news-perex {
          font-size: 13px;
          color: var(--primary-text-color);
          line-height: 1.4;
          display: -webkit-box;
          -webkit-line-clamp: 2;
          -webkit-box-orient: vertical;
          overflow: hidden;
          word-wrap: break-word;
        }
        .no-news {
          padding: 16px;
          text-align: center;
          color: var(--secondary-text-color);
        }
        .loading {
          padding: 16px;
          text-align: center;
          color: var(--secondary-text-color);
        }
        .news-count {
          padding: 8px 16px;
          font-size: 12px;
          color: var(--secondary-text-color);
          text-align: right;
          border-top: 1px solid var(--divider-color);
        }
        @media (max-width: 600px) {
          .news-item {
            flex-direction: column;
          }
          .news-image {
            width: 100%;
            height: 150px;
            margin-right: 0;
            margin-bottom: 8px;
          }
          .csfd-news-container {
            max-height: 500px;
          }
        }
      `;
      card.appendChild(style);

      const content = document.createElement('div');
      content.className = 'csfd-news-container';
      content.id = 'news-container';
      card.appendChild(content);

      const footer = document.createElement('div');
      footer.className = 'news-count';
      footer.id = 'news-count';
      card.appendChild(footer);
    }

    const entityId = this.config.entity;
    const state = hass.states[entityId];

    const container = this.querySelector('#news-container');
    const footer = this.querySelector('#news-count');

    if (!state) {
      container.innerHTML = '<div class="no-news">Entita nenalezena</div>';
      footer.textContent = '';
      return;
    }

    const news = state.attributes.news || [];
    // Display all loaded news by default, or respect config limit
    const maxItems = this.config.max_items !== undefined ? this.config.max_items : news.length;

    if (news.length === 0) {
      container.innerHTML = '<div class="loading">Načítání novinek...</div>';
      footer.textContent = '';
      return;
    }

    // Limit the number of displayed items
    const displayNews = news.slice(0, maxItems);

    container.innerHTML = displayNews.map(item => `
      <div class="news-item" onclick="window.open('${this._escapeHtml(item.link)}', '_blank')">
        ${item.image ? `<img src="${this._escapeHtml(item.image)}" class="news-image" alt="${this._escapeHtml(item.title)}" onerror="this.style.display='none'">` : ''}
        <div class="news-content">
          <div class="news-title">${this._escapeHtml(item.title)}</div>
          ${item.date ? `<div class="news-date">${this._escapeHtml(item.date)}</div>` : ''}
          ${item.perex ? `<div class="news-perex">${this._escapeHtml(item.perex)}</div>` : ''}
        </div>
      </div>
    `).join('');

    footer.textContent = `Zobrazeno ${displayNews.length} z ${news.length} novinek`;
  }

  _escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  setConfig(config) {
    if (!config.entity) {
      throw new Error('Musíte definovat entitu');
    }
    this.config = config;
  }

  getCardSize() {
    return 3;
  }

  static getConfigElement() {
    return document.createElement("csfd-news-card-editor");
  }

  static getStubConfig() {
    return { entity: "sensor.csfd_news" };
  }
}

customElements.define('csfd-news-card', CSFDNewsCard);

window.customCards = window.customCards || [];
window.customCards.push({
  type: 'csfd-news-card',
  name: 'CSFD News Card',
  description: 'Karta pro zobrazení novinek z ČSFD',
  preview: true,
  documentationURL: 'https://github.com/yourusername/csfd-news',
});

console.info(
  '%c CSFD-NEWS-CARD %c 1.0.0 ',
  'color: white; background: #ba0000; font-weight: 700;',
  'color: white; background: #333333; font-weight: 700;'
);
