const test = require('node:test');
const assert = require('node:assert/strict');
const { resolveNarrationSrc, nextLessonInDomain, previousLessonInDomain, parseListeningPosition, nextPlaybackRate, formatTime } = require('./narration-player.js');

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

test('returns the previous lesson in the domain when it has narration', () => {
  const orderedLessons = [
    { id: '2.1', hasNarration: true },
    { id: '2.2', hasNarration: true },
    { id: '2.3', hasNarration: true },
  ];

  assert.equal(previousLessonInDomain('2.3', orderedLessons), '2.2');
});

test('returns null before the domain\'s first lesson', () => {
  const orderedLessons = [
    { id: '2.1', hasNarration: true },
    { id: '2.2', hasNarration: true },
    { id: '2.3', hasNarration: true },
  ];

  assert.equal(previousLessonInDomain('2.1', orderedLessons), null);
});

test('skips a lesson with no narration going backward too', () => {
  const orderedLessons = [
    { id: '1.1', hasNarration: true },
    { id: '1.2', hasNarration: false },
    { id: '1.3', hasNarration: true },
  ];

  assert.equal(previousLessonInDomain('1.3', orderedLessons), '1.1');
});

test('returns null going backward when every earlier lesson lacks narration', () => {
  const orderedLessons = [
    { id: '1.1', hasNarration: false },
    { id: '1.2', hasNarration: true },
  ];

  assert.equal(previousLessonInDomain('1.2', orderedLessons), null);
});

test('parses a valid stored Listening Position', () => {
  const raw = JSON.stringify({ lessonId: '2.3', lang: 'tr', time: 128.5 });

  assert.deepEqual(parseListeningPosition(raw), { lessonId: '2.3', lang: 'tr', time: 128.5 });
});

test('returns null when no Listening Position is stored', () => {
  assert.equal(parseListeningPosition(null), null);
});

test('returns null for malformed stored JSON instead of throwing', () => {
  assert.equal(parseListeningPosition('{not valid json'), null);
});

test('returns null when the stored JSON is missing required fields', () => {
  const raw = JSON.stringify({ lessonId: '2.3' });

  assert.equal(parseListeningPosition(raw), null);
});

test('cycles playback rate from 1x to 1.25x', () => {
  assert.equal(nextPlaybackRate(1), 1.25);
});

test('wraps playback rate from 1.5x back to 1x', () => {
  assert.equal(nextPlaybackRate(1.5), 1);
});

test('formats zero seconds as 0:00', () => {
  assert.equal(formatTime(0), '0:00');
});

test('formats minutes and zero-pads seconds under 10', () => {
  assert.equal(formatTime(75), '1:15');
  assert.equal(formatTime(65), '1:05');
});

test('formats an unknown duration (NaN) as 0:00 instead of throwing', () => {
  assert.equal(formatTime(NaN), '0:00');
});
