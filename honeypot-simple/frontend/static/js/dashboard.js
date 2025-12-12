async function fetchLogs() {
  try {
    const [logsResp, cntResp] = await Promise.all([
      fetch('/api/logs'),
      fetch('/api/logs/count')
    ]);

    const logs = await logsResp.json();
    const cnt = await cntResp.json();

    document.getElementById("summary").innerText = `Total logs: ${cnt.count}`;

    const tbody = document.querySelector("#logsTable tbody");
    tbody.innerHTML = "";

    logs.forEach((r) => {
      const tr = document.createElement("tr");

      tr.innerHTML = `
        <td>${r.id}</td>
        <td>${r.timestamp}</td>
        <td>${r.endpoint}</td>
        <td>${r.ip}</td>
        <td>${r.user_agent}</td>
        <td>${formatBody(r.body)}</td>
        <td>${formatHeaders(r.headers)}</td>
      `;

      tbody.appendChild(tr);
    });

  } catch (err) {
    console.error("Error loading logs:", err);
  }
}

function formatBody(bodyText) {
  if (!bodyText) return "<i>Empty</i>";

  try {
    const obj = JSON.parse(bodyText);
    return `<pre>${JSON.stringify(obj, null, 2)}</pre>`;
  } catch {
    return `<pre>${bodyText}</pre>`;
  }
}

function formatHeaders(headersText) {
  let html = `<table class="subtable">`;

  try {
    const headers = JSON.parse(headersText.replace(/'/g, '"'));

    Object.keys(headers).forEach(key => {
      html += `<tr><td><b>${key}</b></td><td>${headers[key]}</td></tr>`;
    });

  } catch {
    html += `<tr><td colspan="2"><pre>${headersText}</pre></td></tr>`;
  }

  html += `</table>`;
  return html;
}


fetchLogs();
