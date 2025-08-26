// Fetch a puzzle from an API and display it
// Example: Using a riddle API or a static puzzle for demo



document.addEventListener('DOMContentLoaded', function() {
    const puzzleContent = document.getElementById('puzzle-content');
    puzzleContent.innerHTML = 'Loading puzzle...';

    const localPuzzles = [
        { riddle: "I speak without a mouth and hear without ears. I have no body, but I come alive with wind. What am I?", answer: "echo" },
        { riddle: "What has keys but can't open locks?", answer: "piano" },
        { riddle: "What can travel around the world while staying in a corner?", answer: "stamp" }
    ];


    let puzzleCount = 0;
    const maxPuzzles = 3;
    let userAnswers = [];
    let correctCount = 0;

    function fetchPuzzle(callback) {
        // Try to fetch from API, fallback to local
        fetch('https://riddles-api.vercel.app/api/random')
            .then(response => response.json())
            .then(data => {
                if (data && data.riddle && data.answer) {
                    callback(data);
                } else {
                    callback(localPuzzles[puzzleCount % localPuzzles.length]);
                }
            })
            .catch(() => {
                callback(localPuzzles[puzzleCount % localPuzzles.length]);
            });
    }



    function renderPuzzle() {
        if (puzzleCount >= maxPuzzles) {
            puzzleContent.innerHTML = `
                <div style='font-size:1.2em;font-weight:900;color:#388e3c;margin-bottom:1em;'>All puzzles complete!</div>
                <button id="puzzle-submit-score-btn" class="game-submit-btn">Submit Score</button>
                <div id="puzzle-submit-feedback" style="margin-top:1em;"></div>
            `;
            document.getElementById('puzzle-submit-score-btn').onclick = function() {
                let teamNum = window.teamNum || null;
                if (!teamNum) {
                    const teamInput = document.getElementById('team-num');
                    if (teamInput) teamNum = teamInput.value;
                }
                if (!teamNum) {
                    document.getElementById('puzzle-submit-feedback').innerHTML = '<span style="color:red;">Error: Team number not found in session.</span>';
                    return;
                }
                fetch('/submit-level2-score', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ team_num: teamNum, score: correctCount, answers: userAnswers })
                })
                .then(res => res.json())
                .then(data => {
                    if (data.success) {
                        document.getElementById('puzzle-submit-feedback').innerHTML = '<span style="color:green;font-weight:900;">Score submitted! Thank you, Team ' + teamNum + '.</span>';
                    } else {
                        document.getElementById('puzzle-submit-feedback').innerHTML = '<span style="color:red;">Error: ' + (data.error || 'Could not submit score.') + '</span>';
                    }
                })
                .catch(() => {
                    document.getElementById('puzzle-submit-feedback').innerHTML = '<span style="color:red;">Network error.</span>';
                });
            };
            return;
        }
                    puzzleContent.innerHTML = 'Loading puzzle...';
                    fetchPuzzle(function(data) {
                            puzzleContent.innerHTML = `
                                    <div class="puzzle-question">Puzzle ${puzzleCount + 1} of ${maxPuzzles}:<br>${data.riddle}</div>
                                    <input type="text" id="puzzle-answer" placeholder="Enter your answer" style="margin-top:12px;width:90%;padding:8px;border-radius:6px;border:1px solid #ccc;">
                                    <div class="puzzle-btn-row">
                                        <button id="submit-answer" class="game-submit-btn small">Submit</button>
                                    </div>
                                    <div id="puzzle-feedback" style="margin-top:10px;"></div>
                            `;
            document.getElementById('submit-answer').onclick = function() {
                const userAnswer = document.getElementById('puzzle-answer').value.trim();
                userAnswers.push({
                    puzzle: data.riddle,
                    answer: data.answer,
                    user: userAnswer
                });
                const correct = data.answer.trim().toLowerCase();
                const feedback = document.getElementById('puzzle-feedback');
                if (userAnswer.trim().toLowerCase() === correct) {
                    feedback.innerHTML = '<span style="color:green;">Correct! 🎉</span>';
                    correctCount++;
                } else {
                    feedback.innerHTML = '<span style="color:red;">Incorrect! Moving to next puzzle.</span>';
                }
                setTimeout(() => {
                    puzzleCount++;
                    renderPuzzle();
                }, 900);
            };
                    });
            }

        renderPuzzle();
});
