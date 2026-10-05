// Exercise the actual filter script with a minimal DOM contract, no dependencies.
// Browser layout/rendering still requires a real-browser smoke test.
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const root = path.resolve(__dirname, '..');
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'catalog.json'), 'utf8'));
function element(extra = {}) {
  return Object.assign({value:'', hidden:false, listeners:{}, attributes:{},
    addEventListener(name, fn) { this.listeners[name] = fn; },
    setAttribute(name, value) { this.attributes[name] = value; }, focus() {}}, extra);
}
const cards = catalog.items.map(item => element({dataset:{category:item.category,state:item.state,
  search:[item.title,item.description,item.keywords,catalog.categories.find(c=>c.id===item.category).label].join(' ').toLowerCase()}}));
const topics = ['all', ...catalog.categories.map(c => c.id)].map(topic => element({dataset:{topic}}));
const ids = Object.fromEntries(['search','availability','result-count','empty','reset'].map(id=>[id,element()]));
ids.availability.value = 'all';
const document = {getElementById:id=>ids[id],querySelectorAll:selector=>selector==='.card'?cards:topics};
vm.runInNewContext(fs.readFileSync(path.join(root,'assets/app.js'),'utf8'), {document});
const visible = () => cards.filter(card=>!card.hidden);
assert.equal(visible().length, 11);
ids.availability.value='included'; ids.availability.listeners.change();
assert.equal(visible().length, 4);
ids.search.value='CONTACTS'; ids.search.listeners.input();
assert.equal(visible().length, 1);
ids.reset.listeners.click();
topics.find(t=>t.dataset.topic==='maps').listeners.click();
assert.equal(visible().length, 2);
assert.equal(topics.find(t=>t.dataset.topic==='maps').attributes['aria-pressed'], 'true');
ids.availability.value='included'; ids.availability.listeners.change();
assert.equal(visible().length, 0); assert.equal(ids.empty.hidden, false);
ids.reset.listeners.click();
ids.search.value='maps MEMPHIS'; ids.search.listeners.input();
assert.equal(visible().length, 1);
ids.search.value='doesnotexist'; ids.search.listeners.input();
assert.equal(visible().length, 0);
ids.reset.listeners.click(); assert.equal(visible().length, 11);
console.log('Search checks passed: availability, case, topics, combined terms, no results, reset.');
