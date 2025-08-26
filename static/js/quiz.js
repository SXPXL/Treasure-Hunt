// Quiz game logic for quiz.html
let quizQuestions = [];
let quizCurrent = 0;
let quizScore = 0;
let quizPlayer = '';
let quizCategory = '';
let quizDifficulty = '';
let quizType = '';

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
  const quizContainer = document.getElementById('quiz-container');
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
  const quizContainer = document.getElementById('quiz-container');
  quizContainer.innerHTML = `<div style='font-size:1.2em;font-weight:900;margin-bottom:1em;'>Quiz Complete!</div><div style='font-size:1.1em;margin-bottom:1em;'>Score: <b>${quizScore}</b> / ${quizQuestions.length}</div><button id='quiz-submit-score-btn' style='background:#d6af41;color:#fff;font-weight:900;font-size:1.1em;padding:0.6em 2em;border:none;border-radius:0.7em;cursor:pointer;'>Submit Score</button>`;
  document.getElementById('quiz-submit-score-btn').onclick = function() {
    // Get team_num from a hidden input or global JS variable set by Jinja in quiz.html
    let teamNum = window.teamNum || null;
    if (!teamNum) {
      // Try to get from a hidden input (if rendered by Jinja)
      const teamInput = document.getElementById('team-num');
      if (teamInput) teamNum = teamInput.value;
    }
    if (!teamNum) {
      quizContainer.innerHTML += `<div style='color:#e57373;'>Error: Team number not found in session.</div>`;
      return;
    }
    fetch('/submit-level1-score', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ team_num: teamNum, score: quizScore })
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        quizContainer.innerHTML = `<div style='font-size:1.1em;color:#388e3c;font-weight:900;'>Score submitted! Thank you, Team ${teamNum}.</div>`;
      } else {
        quizContainer.innerHTML += `<div style='color:#e57373;'>Error: ${data.error || 'Could not submit score.'}</div>`;
      }
    })
    .catch(() => {
      quizContainer.innerHTML += `<div style='color:#e57373;'>Network error.</div>`;
    });
  };
}

function startQuizFromParams() {
  const params = new URLSearchParams(window.location.search);
  quizPlayer = params.get('player') || 'Player';
  quizCategory = params.get('category') || '9';
  quizDifficulty = params.get('difficulty') || 'medium';
  quizType = params.get('type') || 'multiple';
  fetch(`https://opentdb.com/api.php?amount=3&category=${quizCategory}&difficulty=${quizDifficulty}&type=${quizType}`)
    .then(res => res.json())
    .then(data => {
      if (data.results && data.results.length > 0) {
        quizQuestions = data.results;
        quizCurrent = 0;
        quizScore = 0;
        renderQuizQuestion();
      } else {
        document.getElementById('quiz-container').innerHTML = '<div style="color:#e57373;">No questions found for these settings.</div>';
      }
    })
    .catch(() => {
      document.getElementById('quiz-container').innerHTML = '<div style="color:#e57373;">Failed to load questions.</div>';
    });
}

document.addEventListener('DOMContentLoaded', startQuizFromParams);
