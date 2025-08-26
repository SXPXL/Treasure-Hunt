// JS separated from admin_leaderboard.html
function openDrawer() {
    document.getElementById('drawerMenu').classList.add('open');
    document.getElementById('drawerOverlay').classList.add('open');
}
function closeDrawer() {
    document.getElementById('drawerMenu').classList.remove('open');
    document.getElementById('drawerOverlay').classList.remove('open');
}

// Fetch scores for all teams from all level tables, sum, and update users table
async function updateAllTeamScores() {
    async function fetchLevelScores(levelTable) {
        const response = await fetch(`/get_level_scores?table=${levelTable}`);
        return response.ok ? await response.json() : [];
    }
    const levels = ['level1_scores', 'level2_scores', 'level3_scores', 'level4_scores'];
    const allScores = {};
    for (const level of levels) {
        const scores = await fetchLevelScores(level);
        for (const entry of scores) {
            if (!allScores[entry.team_num]) allScores[entry.team_num] = 0;
            allScores[entry.team_num] += 1; // Each entry counts as 1 point
        }
    }
    await fetch('/update_team_scores', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(allScores)
    });
    alert('Scores updated!');
}
// To use: add a button in HTML and call updateAllTeamScores on click
// Example: <button onclick="updateAllTeamScores()">Update Scores</button>
