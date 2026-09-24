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

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { resolveNarrationSrc, nextLessonInDomain, previousLessonInDomain, parseListeningPosition };
}
