const test = require('node:test');
const assert = require('node:assert/strict');
const { resolveNarrationSrc, nextLessonInDomain } = require('./narration-player.js');

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

test('returns the next lesson in the domain when it has narration', () => {
  const orderedLessons = [
    { id: '2.1', hasNarration: true },
    { id: '2.2', hasNarration: true },
    { id: '2.3', hasNarration: true },
  ];

  assert.equal(nextLessonInDomain('2.1', orderedLessons), '2.2');
});

test('returns null after the domain\'s last lesson (no cross-domain continuation)', () => {
  const orderedLessons = [
    { id: '2.1', hasNarration: true },
    { id: '2.2', hasNarration: true },
    { id: '2.3', hasNarration: true },
  ];

  assert.equal(nextLessonInDomain('2.3', orderedLessons), null);
});

test('skips a lesson with no narration in the active language and advances to the next available one', () => {
  const orderedLessons = [
    { id: '1.1', hasNarration: true },
    { id: '1.2', hasNarration: true },
    { id: '1.3', hasNarration: false },
    { id: '1.4', hasNarration: true },
  ];

  assert.equal(nextLessonInDomain('1.2', orderedLessons), '1.4');
});

test('returns null when every remaining lesson lacks narration', () => {
  const orderedLessons = [
    { id: '1.1', hasNarration: true },
    { id: '1.2', hasNarration: true },
    { id: '1.3', hasNarration: false },
  ];

  assert.equal(nextLessonInDomain('1.2', orderedLessons), null);
});
