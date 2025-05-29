let gazeData = [];
const heatmap = h337.create({
  container: document.getElementById('heatmapContainer'),
  radius: 40,
  maxOpacity: 0.6,
  minOpacity: 0,
  blur: 0.75,
});

window.onload = () => {
  webgazer.setGazeListener((data, timestamp) => {
    if (data) {
      const x = data.x;
      const y = data.y;

      // Store gaze point
      gazeData.push({ x, y, timestamp });

      // Add to heatmap
      heatmap.addData({ x, y, value: 1 });

      drawDot(x, y);
    }
  }).begin();
};

function drawDot(x, y) {
  const canvas = document.getElementById('overlay');
  const ctx = canvas.getContext('2d');
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.beginPath();
  ctx.arc(x, y, 10, 0, 2 * Math.PI);
  ctx.fillStyle = 'red';
  ctx.fill();
}

function downloadData() {
  const blob = new Blob([JSON.stringify(gazeData)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = "gazeData.json";
  a.click();
}