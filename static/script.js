const tabs = document.querySelectorAll(".tab-link");
const panes = document.querySelectorAll(".tab-pane");

function clearTabs() {
  tabs.forEach(t => t.classList.remove("active"));
  panes.forEach(p => p.classList.remove("active"));
}

function showTab(tabId) {
  clearTabs();
  document.querySelector([data-tab='${tabId}']).classList.add("active");
  document.getElementById(tabId).classList.add("active");

  if (tabId === "explorer") fetchBlockchain();
  else if (tabId === "pending") fetchPendingTransactions();
  else if (tabId === "validity") checkValidity();
  else if (tabId === "mine") checkMineStatus();
}

tabs.forEach(tab => {
  tab.addEventListener("click", () => {
    showTab(tab.dataset.tab);
  });
});

async function fetchBlockchain() {
  const blockchainView = document.getElementById("blockchainView");
  try {
    const response = await fetch("/chain");
    const data = await response.json();

    if (!data.length) {
      blockchainView.textContent = "Blockchain is empty.";
      return;
    }

    const output = data.map(block => {
      const txns = block.transactions.map(tx => `  - ${tx.sender} → ${tx.recipient}: ${tx.amount}`).join("\n");
      const timestamp = new Date(block.timestamp * 1000).toLocaleString();
      return `Block #${block.index} [${timestamp}]
Hash:       ${block.hash}
Prev Hash:  ${block.previous_hash}
Nonce:      ${block.nonce}
Transactions:
${txns}\n`;
    }).join("\n-----------------------\n\n");

    blockchainView.textContent = output;
  } catch (e) {
    blockchainView.textContent = "Failed to load blockchain.";
  }
}

async function fetchPendingTransactions() {
  const pendingView = document.getElementById("pendingTransactions");
  try {
    const response = await fetch("/pending");
    const data = await response.json();

    if (!data.length) {
      pendingView.textContent = "No pending transactions.";
      return;
    }

    const output = data.map(tx => ${tx.sender} → ${tx.recipient}: ${tx.amount}).join("\n");
    pendingView.textContent = output;
  } catch (e) {
    pendingView.textContent = "Failed to load pending transactions.";
  }
}

async function checkValidity() {
  const validityStatus = document.getElementById("validityStatus");
  validityStatus.textContent = "Checking blockchain validity...";
  try {
    const response = await fetch("/valid");
    const data = await response.json();
    if (data.valid) {
      validityStatus.style.color = "#4CAF50"; // green
      validityStatus.textContent = "Blockchain is valid. 👍";
    } else {
      validityStatus.style.color = "#f44336"; // red
      validityStatus.textContent = "Blockchain is NOT valid! ⚠";
    }
  } catch (e) {
    validityStatus.style.color = "#f44336";
    validityStatus.textContent = "Failed to check validity.";
  }
}

function checkMineStatus() {
  const mineButton = document.getElementById("mineButton");
  const mineStatus = document.getElementById("mineStatus");

  // Simple check if there are any pending transactions before enabling mine button
  fetch("/pending").then(res => res.json()).then(data => {
    if (data.length === 0) {
      mineButton.disabled = true;
      mineStatus.textContent = "No transactions to mine.";
    } else {
      mineButton.disabled = false;
      mineStatus.textContent = "";
    }
  }).catch(() => {
    mineButton.disabled = false;
    mineStatus.textContent = "";
  });
}

// Show "Send" tab by default on load
showTab("send");