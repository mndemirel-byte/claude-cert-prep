function resolveNarrationSrc(dataset, lang) {
  if (lang === 'en') return dataset.narrationEn || null;
  if (lang === 'tr') return dataset.narrationTr || null;
  return null;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { resolveNarrationSrc };
}
