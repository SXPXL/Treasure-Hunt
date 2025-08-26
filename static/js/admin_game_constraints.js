function openDrawer() {
  document.getElementById('drawerMenu').classList.add('open');
  document.getElementById('drawerMenu').setAttribute('aria-hidden', 'false');
  document.getElementById('drawerMenu').focus();
  document.getElementById('drawerOverlay').classList.add('open');
  document.getElementById('hamburgerBtn').setAttribute('aria-expanded', 'true');

// --- Quiz Game Logic ---
const quizSection = document.getElementById('quiz-game-section');
const quizStartBtn = document.getElementById('quiz-start-btn');
const quizContainer = document.getElementById('quiz-container');
let quizQuestions = [];
let quizCurrent = 0;
let quizScore = 0;
let quizPlayer = '';

function shuffleArray(array) {
  for (let i = array.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [array[i], array[j]] = [array[j], array[i]];
  }
}

function decodeHTMLEntities(text) {
  var txt = document.createElement('textarea');
  txt.innerHTML = text;
  return txt.value;
}

function renderQuizQuestion() {
  if (quizCurrent >= quizQuestions.length) {
    renderQuizResult();
    return;
  }
  const q = quizQuestions[quizCurrent];
  let answers = q.incorrect_answers.map(decodeHTMLEntities);
  answers.push(decodeHTMLEntities(q.correct_answer));
  shuffleArray(answers);
  let html = `<div style='font-size:1.1em;font-weight:700;margin-bottom:1em;'>Q${quizCurrent+1}: ${decodeHTMLEntities(q.question)}</div>`;
  html += `<div style='display:flex;flex-direction:column;gap:1em;'>`;
  answers.forEach(ans => {
    html += `<button class='quiz-answer-btn' style='padding:0.7em 1em;font-size:1em;border-radius:0.7em;border:2px solid #d6af41;background:#fffbe6;cursor:pointer;' data-answer="${ans}">${ans}</button>`;
  });
  html += `</div>`;
  quizContainer.innerHTML = html;
  document.querySelectorAll('.quiz-answer-btn').forEach(btn => {
    btn.onclick = function() {
      const selected = btn.getAttribute('data-answer');
      const correct = decodeHTMLEntities(q.correct_answer);
      if (selected === correct) {
        quizScore++;
        btn.style.background = '#d6af41';
        btn.style.color = '#fff';
      } else {
        btn.style.background = '#e57373';
        btn.style.color = '#fff';
      }
      document.querySelectorAll('.quiz-answer-btn').forEach(b => b.disabled = true);
      setTimeout(() => {
        quizCurrent++;
        renderQuizQuestion();
      }, 900);
    };
  });
}

function renderQuizResult() {
  quizContainer.innerHTML = `<div style='font-size:1.2em;font-weight:900;margin-bottom:1em;'>Quiz Complete!</div><div style='font-size:1.1em;margin-bottom:1em;'>Score: <b>${quizScore}</b> / ${quizQuestions.length}</div><button id='quiz-submit-score-btn' style='background:#d6af41;color:#fff;font-weight:900;font-size:1.1em;padding:0.6em 2em;border:none;border-radius:0.7em;cursor:pointer;'>Submit Score</button>`;
  document.getElementById('quiz-submit-score-btn').onclick = function() {
    fetch('/submit-score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ player: quizPlayer, score: quizScore })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        quizContainer.innerHTML = `<div style='font-size:1.1em;color:#388e3c;font-weight:900;'>Score submitted! Thank you, ${quizPlayer}.</div>`;
      } else {
        quizContainer.innerHTML += `<div style='color:#e57373;'>Error: ${data.error || 'Could not submit score.'}</div>`;
      }
    })
    .catch(() => {
      quizContainer.innerHTML += `<div style='color:#e57373;'>Network error.</div>`;
    });
  };
}

if (quizStartBtn) {
  quizStartBtn.onclick = function() {
    const category = document.getElementById('quiz-category').value;
    const difficulty = document.getElementById('quiz-difficulty').value;
    const type = document.getElementById('quiz-type').value;
    quizPlayer = document.getElementById('quiz-player-name').value.trim() || 'Player';
    quizStartBtn.disabled = true;
    quizStartBtn.textContent = 'Loading...';
    quizContainer.innerHTML = '';
    fetch(`https://opentdb.com/api.php?amount=10&category=${category}&difficulty=${difficulty}&type=${type}`)
      .then(res => res.json())
      .then(data => {
        if (data.results && data.results.length > 0) {
          quizQuestions = data.results;
          quizCurrent = 0;
          quizScore = 0;
          renderQuizQuestion();
        } else {
          quizContainer.innerHTML = '<div style="color:#e57373;">No questions found for these settings.</div>';
        }
      })
      .catch(() => {
        quizContainer.innerHTML = '<div style="color:#e57373;">Failed to load questions.</div>';
      })
      .finally(() => {
        quizStartBtn.disabled = false;
        quizStartBtn.textContent = 'Start Quiz';
      });
  };
}
function closeDrawer() {
  document.getElementById('drawerMenu').classList.remove('open');
  document.getElementById('drawerMenu').setAttribute('aria-hidden', 'true');
  document.getElementById('drawerOverlay').classList.remove('open');
  document.getElementById('hamburgerBtn').setAttribute('aria-expanded', 'false');
}
