const test = require('node:test');
const assert = require('node:assert/strict');
const { resolveNarrationSrc } = require('./narration-player.js');

test('returns the narration url matching the active language', () => {
  const dataset = { narrationEn: 'audio/en/D2-1.mp3', narrationTr: 'audio/tr/D2-1.mp3' };

  assert.equal(resolveNarrationSrc(dataset, 'en'), 'audio/en/D2-1.mp3');
});

test('returns the tr narration url when tr is active', () => {
  const dataset = { narrationEn: 'audio/en/D2-1.mp3', narrationTr: 'audio/tr/D2-1.mp3' };

  assert.equal(resolveNarrationSrc(dataset, 'tr'), 'audio/tr/D2-1.mp3');
});

test('returns null when the active language has no narration', () => {
  const dataset = { narrationTr: 'audio/tr/D1-3.mp3' };

  assert.equal(resolveNarrationSrc(dataset, 'en'), null);
});
