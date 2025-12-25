async function loadLogs() {

  const [allRes, attackRes, countRes] = await Promise.all([
    fetch("/api/logs"),
    fetch("/api/logs/attacks"),
    fetch("/api/logs/count")
  ]);

  const allLogs = await allRes.json();
  const attackLogs = await attackRes.json();
  const count = await countRes.json();

  document.getElementById("count").innerText = count.count;

  const attackBody = document.getElementById("attackLogs");
  attackBody.innerHTML = "";

  attackLogs.forEach(l => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${l.timestamp}</td>
      <td>${l.ip}</td>
      <td>${l.method}</td>
      <td>${l.endpoint}</td>
      <td>${l.user_agent}</td>
    `;
    attackBody.appendChild(tr);
  });

  const allBody = document.getElementById("allLogs");
  allBody.innerHTML = "";

  allLogs.forEach(l => {
    const tr = document.createElement("tr");
    tr.innerHTML = `
      <td>${l.timestamp}</td>
      <td>${l.ip}</td>
      <td>${l.method}</td>
      <td>${l.endpoint}</td>
    `;
    allBody.appendChild(tr);
  });
}

// load once (NO polling spam)
loadLogs();
