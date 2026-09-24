var ALL_SCENARIOS = [1, 2, 3, 4, 5, 6];

function combinations(items, k) {
  if (k === 0) return [[]];
  if (items.length < k) return [];
  var [first, ...rest] = items;
  var withFirst = combinations(rest, k - 1).map(function (c) { return [first].concat(c); });
  var withoutFirst = combinations(rest, k);
  return withFirst.concat(withoutFirst);
}

function viableScenarioCombos(pool, domainTargets) {
  var combos = combinations(ALL_SCENARIOS, 4);
  return combos.filter(function (combo) {
    return Object.keys(domainTargets).every(function (d) {
      d = Number(d);
      var supply = pool.filter(function (q) { return q.d === d && combo.indexOf(q.sc) !== -1; }).length;
      return supply >= domainTargets[d];
    });
  });
}

function shuffle(arr) {
  var a = arr.slice();
  for (var i = a.length - 1; i > 0; i--) {
    var j = Math.floor(Math.random() * (i + 1));
    var t = a[i]; a[i] = a[j]; a[j] = t;
  }
  return a;
}

function sampleExamQuestions(pool, combo, domainTargets) {
  var questions = [];
  Object.keys(domainTargets).forEach(function (d) {
    d = Number(d);
    var candidates = pool.filter(function (q) { return q.d === d && combo.indexOf(q.sc) !== -1; });
    questions = questions.concat(shuffle(candidates).slice(0, domainTargets[d]));
  });
  return questions;
}

var LETTERS = ['A', 'B', 'C', 'D'];

function shuffleQuestionOptions(question) {
  var texts = LETTERS.map(function (k) { return question.opts[k]; });
  var correctText = question.opts[question.ans];
  var order = shuffle(LETTERS);
  var newOpts = {};
  var newAns = null;
  order.forEach(function (letter, i) {
    newOpts[letter] = texts[i];
    if (texts[i] === correctText) newAns = letter;
  });
  return Object.assign({}, question, { opts: newOpts, ans: newAns });
}

function orderByScenario(questions) {
  var byScenario = {};
  var scenarios = [];
  questions.forEach(function (q) {
    if (!byScenario[q.sc]) { byScenario[q.sc] = []; scenarios.push(q.sc); }
    byScenario[q.sc].push(q);
  });
  var ordered = [];
  shuffle(scenarios).forEach(function (sc) {
    ordered = ordered.concat(shuffle(byScenario[sc]));
  });
  return ordered;
}

if (typeof module !== 'undefined' && module.exports) {
  module.exports = { viableScenarioCombos, sampleExamQuestions, shuffleQuestionOptions, orderByScenario };
}
