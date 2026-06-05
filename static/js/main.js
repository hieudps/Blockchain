let charts = {};
let currentWallet = localStorage.getItem("currentWallet") || "";

function showToast(message, type = "ok") {
    const toast = document.getElementById("toast");
    toast.textContent = message;
    toast.className = `toast show ${type}`;
    setTimeout(() => toast.className = "toast", 2600);
}

async function api(url, options = {}) {
    const response = await fetch(url, {
        headers: { "Content-Type": "application/json" },
        ...options
    });
    const data = await response.json();

    if (!response.ok || data.success === false) {
        throw new Error(data.message || "Request failed");
    }

    return data;
}

function formatTime(timestamp) {
    return new Date(timestamp * 1000).toLocaleString("vi-VN");
}

function shortAddress(address = "") {
    if (address.length <= 18) return address;
    return `${address.slice(0, 10)}...${address.slice(-6)}`;
}

function transactionBadge(type, sender) {
    if (type === "reward") return "reward";
    if (sender === currentWallet) return "sent";
    return "received";
}

async function createWallet() {
    try {
        const label = document.getElementById("walletLabel").value;
        const initial_balance = Number(document.getElementById("walletInitial").value || 0);
        const data = await api("/api/wallet/create", {
            method: "POST",
            body: JSON.stringify({ label, initial_balance })
        });
        setCurrentWallet(data.wallet.address);
        document.getElementById("sender").value = data.wallet.address;
        document.getElementById("minerAddress").value = data.wallet.address;
        showToast("Wallet created");
        await refreshAll();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function loginWallet(address = null) {
    try {
        const walletAddress = address || document.getElementById("loginAddress").value;
        const data = await api("/api/wallet/login", {
            method: "POST",
            body: JSON.stringify({ address: walletAddress })
        });
        setCurrentWallet(data.wallet.address);
        document.getElementById("sender").value = data.wallet.address;
        document.getElementById("minerAddress").value = data.wallet.address;
        showToast("Wallet logged in");
        await refreshAll();
    } catch (error) {
        showToast(error.message, "error");
    }
}

function setCurrentWallet(address) {
    currentWallet = address;
    localStorage.setItem("currentWallet", address);
    document.getElementById("currentWalletText").textContent = `Current wallet: ${address || "none"}`;
}

async function loadWallets() {
    const data = await api("/api/wallets");
    const list = document.getElementById("walletList");

    if (!data.wallets.length) {
        list.innerHTML = "<p class='empty'>No wallets yet</p>";
        return;
    }

    list.innerHTML = data.wallets.map(wallet => `
        <div class="wallet-item ${wallet.address === currentWallet ? "active" : ""}">
            <div>
                <strong>${wallet.label}</strong>
                <span>${wallet.address}</span>
            </div>
            <button onclick="loginWallet('${wallet.address}')">Use</button>
        </div>
    `).join("");
}

async function sendTransaction() {
    try {
        const sender = document.getElementById("sender").value || currentWallet;
        const receiver = document.getElementById("receiver").value;
        const amount = Number(document.getElementById("amount").value);

        await api("/api/transaction", {
            method: "POST",
            body: JSON.stringify({ sender, receiver, amount })
        });

        showToast("Transaction added to pending pool");
        document.getElementById("amount").value = "";
        await refreshAll();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function mineBlock() {
    const button = document.getElementById("mineButton");
    const progress = document.getElementById("mineProgress");
    const result = document.getElementById("mineResult");
    const miner = document.getElementById("minerAddress").value || currentWallet;

    button.disabled = true;
    progress.style.width = "15%";
    result.innerHTML = "<p>Mining in progress...</p>";

    const interval = setInterval(() => {
        const current = parseInt(progress.style.width || "15", 10);
        progress.style.width = `${Math.min(current + 12, 92)}%`;
    }, 250);

    try {
        const data = await api("/api/mine", {
            method: "POST",
            body: JSON.stringify({ miner })
        });
        progress.style.width = "100%";
        result.innerHTML = `
            <p><strong>Block #${data.block.index}</strong> mined in ${data.mining_time}s</p>
            <p>Reward: ${data.reward} | Miner balance: ${data.miner_balance}</p>
            <code>${data.block.hash}</code>
        `;
        showToast("Block mined successfully");
        await refreshAll();
    } catch (error) {
        result.innerHTML = `<p class="error-text">${error.message}</p>`;
        showToast(error.message, "error");
    } finally {
        clearInterval(interval);
        button.disabled = false;
        setTimeout(() => progress.style.width = "0%", 900);
    }
}

async function loadChain() {
    const data = await api("/api/chain");
    renderBlocks(data.chain);
    renderPending(data.pending_transactions_list || []);
    return data;
}

function renderBlocks(chain) {
    const list = document.getElementById("blockList");
    list.innerHTML = chain.slice().reverse().map(block => `
        <article class="block-card">
            <div class="block-head">
                <strong>Block #${block.index}</strong>
                <span>${block.transactions.length} tx</span>
            </div>
            <p><b>Hash:</b> <code>${block.hash}</code></p>
            <p><b>Previous:</b> <code>${block.previous_hash}</code></p>
            <p><b>Nonce:</b> ${block.nonce} | <b>Time:</b> ${formatTime(block.timestamp)}</p>
            <div class="mini-table">
                ${block.transactions.map(tx => `
                    <div class="tx-row ${transactionBadge(tx.type, tx.sender)}">
                        <span>${tx.type || "transfer"}</span>
                        <span>${shortAddress(tx.sender)} -> ${shortAddress(tx.receiver)}</span>
                        <strong>${tx.amount}</strong>
                    </div>
                `).join("")}
            </div>
        </article>
    `).join("");
}

function renderPending(pending) {
    const list = document.getElementById("pendingList");
    if (!pending.length) {
        list.innerHTML = "<p class='empty'>Pending pool is empty</p>";
        return;
    }

    list.innerHTML = `
        <table>
            <thead><tr><th>Sender</th><th>Receiver</th><th>Amount</th><th>Gas</th><th>Time</th></tr></thead>
            <tbody>
                ${pending.map(tx => `
                    <tr>
                        <td>${shortAddress(tx.sender)}</td>
                        <td>${shortAddress(tx.receiver)}</td>
                        <td>${tx.amount}</td>
                        <td>${tx.gas_fee}</td>
                        <td>${formatTime(tx.timestamp)}</td>
                    </tr>
                `).join("")}
            </tbody>
        </table>
    `;
}

async function searchAddress() {
    try {
        const address = document.getElementById("searchAddress").value;
        const data = await api(`/api/address/${encodeURIComponent(address)}/transactions`);
        const result = document.getElementById("addressResult");

        if (!data.transactions.length) {
            result.innerHTML = `<p><strong>Balance:</strong> ${data.balance}</p><p class="empty">No transactions found</p>`;
            return;
        }

        result.innerHTML = `
            <p><strong>Balance:</strong> ${data.balance}</p>
            <table>
                <thead><tr><th>Status</th><th>Block</th><th>Type</th><th>Sender</th><th>Receiver</th><th>Amount</th><th>Gas</th><th>Time</th></tr></thead>
                <tbody>
                    ${data.transactions.map(tx => `
                        <tr>
                            <td><span class="pill ${tx.status}">${tx.status}</span></td>
                            <td>${tx.block === null ? "-" : tx.block}</td>
                            <td>${tx.type}</td>
                            <td>${shortAddress(tx.sender)}</td>
                            <td>${shortAddress(tx.receiver)}</td>
                            <td>${tx.amount}</td>
                            <td>${tx.gas_fee}</td>
                            <td>${formatTime(tx.timestamp)}</td>
                        </tr>
                    `).join("")}
                </tbody>
            </table>
        `;
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function validateChain() {
    try {
        const data = await api("/api/validate");
        const result = document.getElementById("validateResult");
        result.innerHTML = data.valid
            ? "<p class='success-text'>Blockchain hop le</p>"
            : `<p class='error-text'>Blockchain khong hop le</p>${data.errors.map(error => `<p>Block #${error.block}: ${error.message}</p>`).join("")}`;
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function tamperBlock() {
    try {
        const block_index = Number(document.getElementById("tamperIndex").value);
        const amount = document.getElementById("tamperAmount").value;
        const data = await api("/api/tamper", {
            method: "POST",
            body: JSON.stringify({ block_index, amount })
        });
        showToast(data.message);
        await loadChain();
        await validateChain();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function updateDifficulty() {
    try {
        const difficulty = Number(document.getElementById("difficultyInput").value);
        const data = await api("/api/settings/difficulty", {
            method: "POST",
            body: JSON.stringify({ difficulty })
        });
        showToast(`Difficulty updated to ${data.difficulty}`);
        await refreshAll();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function resetBlockchain() {
    if (!confirm("Reset all blockchain data and create a new genesis block?")) return;

    try {
        await api("/api/reset", { method: "POST", body: "{}" });
        currentWallet = "";
        localStorage.removeItem("currentWallet");
        showToast("Blockchain reset");
        await refreshAll();
    } catch (error) {
        showToast(error.message, "error");
    }
}

async function loadAdvancedStats() {
    const data = await api("/api/stats/advanced");
    document.getElementById("statBlocks").textContent = data.total_blocks;
    document.getElementById("statTx").textContent = data.total_transactions;
    document.getElementById("statPending").textContent = data.pending_transactions;
    document.getElementById("statWallets").textContent = data.total_wallets;
    document.getElementById("statDifficulty").textContent = data.difficulty;
    document.getElementById("statReward").textContent = data.mining_reward;
    document.getElementById("rewardRule").textContent = data.mining_reward;
    document.getElementById("gasRule").textContent = data.gas_fee;
    document.getElementById("difficultyRule").textContent = data.difficulty;
    document.getElementById("difficultyInput").value = data.difficulty;
    setCurrentWallet(currentWallet || data.current_wallet || "");
    renderCharts(data);
}

function renderCharts(data) {
    makeChart("blocksChart", "line", {
        labels: data.blocks_by_time.map(item => `#${item.block}`),
        datasets: [{
            label: "Block height",
            data: data.blocks_by_time.map((_, index) => index + 1),
            borderColor: "#5eead4",
            backgroundColor: "rgba(94, 234, 212, 0.18)",
            fill: true,
            tension: 0.35
        }]
    });

    makeChart("txChart", "bar", {
        labels: data.transactions_per_block.map(item => `#${item.block}`),
        datasets: [{
            label: "Transactions",
            data: data.transactions_per_block.map(item => item.transactions),
            backgroundColor: "#f59e0b"
        }]
    });

    makeChart("balanceChart", "bar", {
        labels: data.wallet_balances.map(item => item.label),
        datasets: [{
            label: "Balance",
            data: data.wallet_balances.map(item => item.balance),
            backgroundColor: "#60a5fa"
        }]
    });
}

function makeChart(id, type, data) {
    const canvas = document.getElementById(id);
    if (!canvas) return;
    if (charts[id]) charts[id].destroy();

    charts[id] = new Chart(canvas.getContext("2d"), {
        type,
        data,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: "#d7dde8" } } },
            scales: {
                x: { ticks: { color: "#9aa7b7" }, grid: { color: "rgba(255,255,255,0.06)" } },
                y: { ticks: { color: "#9aa7b7" }, grid: { color: "rgba(255,255,255,0.06)" } }
            }
        }
    });
}

async function refreshAll() {
    try {
        await loadWallets();
        await loadChain();
        await loadAdvancedStats();
    } catch (error) {
        showToast(error.message, "error");
    }
}

window.addEventListener("load", () => {
    setCurrentWallet(currentWallet);
    if (currentWallet) {
        document.getElementById("sender").value = currentWallet;
        document.getElementById("minerAddress").value = currentWallet;
    }
    refreshAll();
});
