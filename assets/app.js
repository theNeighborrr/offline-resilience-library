'use strict';
(() => {
  const query = document.getElementById('search');
  const availability = document.getElementById('availability');
  const cards = [...document.querySelectorAll('.card')];
  const topics = [...document.querySelectorAll('[data-topic]')];
  const count = document.getElementById('result-count');
  const empty = document.getElementById('empty');
  let category = 'all';

  function filter() {
    const terms = query.value.toLocaleLowerCase().trim().split(/\s+/).filter(Boolean);
    let shown = 0;
    cards.forEach(card => {
      const match = (category === 'all' || card.dataset.category === category)
        && (availability.value === 'all' || card.dataset.state === availability.value)
        && terms.every(term => card.dataset.search.includes(term));
      card.hidden = !match;
      if (match) shown++;
    });
    count.textContent = `${shown} ${shown === 1 ? 'item' : 'items'} shown`;
    empty.hidden = shown !== 0;
    topics.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.topic === category)));
  }

  query.addEventListener('input', filter);
  availability.addEventListener('change', filter);
  topics.forEach(button => button.addEventListener('click', () => { category = button.dataset.topic; filter(); }));
  document.getElementById('reset').addEventListener('click', () => {
    category = 'all'; query.value = ''; availability.value = 'all'; filter(); query.focus();
  });
  filter();
})();

