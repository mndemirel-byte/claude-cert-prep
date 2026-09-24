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

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { resolveNarrationSrc, nextLessonInDomain };
}
