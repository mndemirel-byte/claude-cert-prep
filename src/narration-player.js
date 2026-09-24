function resolveNarrationSrc(dataset, lang) {
  if (lang === 'en') return dataset.narrationEn || null;
  if (lang === 'tr') return dataset.narrationTr || null;
  return null;
}

function nextLessonInDomain(currentId, orderedLessons) {
  var i = orderedLessons.findIndex(function (l) { return l.id === currentId; });
  for (var j = i + 1; j < orderedLessons.length; j++) {
    if (orderedLessons[j].hasNarration) return orderedLessons[j].id;
  }
  return null;
}

function previousLessonInDomain(currentId, orderedLessons) {
  var i = orderedLessons.findIndex(function (l) { return l.id === currentId; });
  for (var j = i - 1; j >= 0; j--) {
    if (orderedLessons[j].hasNarration) return orderedLessons[j].id;
  }
  return null;
}

function parseListeningPosition(raw) {
  if (!raw) return null;
  var parsed;
  try { parsed = JSON.parse(raw); } catch (e) { return null; }
  if (typeof parsed.lessonId !== 'string' || typeof parsed.lang !== 'string' || typeof parsed.time !== 'number') {
    return null;
  }
  return { lessonId: parsed.lessonId, lang: parsed.lang, time: parsed.time };
}

var PLAYBACK_RATES = [1, 1.25, 1.5];

function nextPlaybackRate(current) {
  var i = PLAYBACK_RATES.indexOf(current);
  return PLAYBACK_RATES[(i + 1) % PLAYBACK_RATES.length];
}

function formatTime(seconds) {
  if (!isFinite(seconds)) return '0:00';
  var s = Math.floor(seconds);
  var m = Math.floor(s / 60);
  var r = s % 60;
  return m + ':' + (r < 10 ? '0' : '') + r;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { resolveNarrationSrc, nextLessonInDomain, previousLessonInDomain, parseListeningPosition, nextPlaybackRate, formatTime };
}
