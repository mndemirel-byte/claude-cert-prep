const test = require('node:test');
const assert = require('node:assert/strict');
const { viableScenarioCombos, sampleExamQuestions } = require('./mock-builder.js');

function abundantPool() {
  const pool = [];
  for (let sc = 1; sc <= 6; sc++) {
    for (let d = 1; d <= 5; d++) {
      for (let i = 0; i < 10; i++) pool.push({ d, sc });
    }
  }
  return pool;
}

test('returns all 15 combos when every domain has abundant supply everywhere', () => {
  const combos = viableScenarioCombos(abundantPool(), { 1: 2, 2: 2, 3: 2, 4: 2, 5: 2 });

  assert.equal(combos.length, 15);
});

test('excludes combos that cannot supply a domain clustered in only 1-2 scenarios', () => {
  // Domain 3 only exists in scenario 2 (47 questions) and scenario 5 (10 questions),
  // mirroring the real clustering case found during spec grilling. Target is 12.
  const pool = abundantPool()
    .filter((q) => q.d !== 3)
    .concat(
      Array.from({ length: 47 }, () => ({ d: 3, sc: 2 })),
      Array.from({ length: 10 }, () => ({ d: 3, sc: 5 }))
    );

  const combos = viableScenarioCombos(pool, { 1: 2, 2: 2, 3: 12, 4: 2, 5: 2 });

  // every viable combo must include scenario 2 (5 alone only supplies 10 < 12)
  assert.ok(combos.every((c) => c.includes(2)));
  assert.equal(combos.length, 10);
  assert.ok(!combos.some((c) => !c.includes(2) && !c.includes(5)));
});

test('samples the exact per-domain target counts from the combo', () => {
  const pool = abundantPool();
  const combo = [1, 2, 3, 4];

  const questions = sampleExamQuestions(pool, combo, { 1: 3, 2: 2, 3: 1, 4: 4, 5: 0 });

  const countByDomain = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
  questions.forEach((q) => { countByDomain[q.d]++; });
  assert.deepEqual(countByDomain, { 1: 3, 2: 2, 3: 1, 4: 4, 5: 0 });
});

test('only draws questions from scenarios in the chosen combo', () => {
  const pool = abundantPool();
  const combo = [1, 2, 3, 4]; // scenarios 5 and 6 excluded

  const questions = sampleExamQuestions(pool, combo, { 1: 10, 2: 10, 3: 10, 4: 10, 5: 0 });

  assert.ok(questions.every((q) => combo.includes(q.sc)));
});

test('never selects the same question twice', () => {
  const pool = [];
  for (let i = 0; i < 5; i++) pool.push({ d: 1, sc: 1, id: 'q' + i });
  const combo = [1, 2, 3, 4];

  const questions = sampleExamQuestions(pool, combo, { 1: 5, 2: 0, 3: 0, 4: 0, 5: 0 });

  assert.equal(new Set(questions.map((q) => q.id)).size, 5);
});
