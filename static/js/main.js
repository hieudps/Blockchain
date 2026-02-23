let chart;

function showToast(message){
    const toast = document.getElementById("toast");
    toast.innerText = message;
    toast.style.display = "block";
    setTimeout(()=> toast.style.display="none",2000);
}

async function transfer(){

    const sender = document.getElementById("sender").value;
    const receiver = document.getElementById("receiver").value;
    const amount = parseInt(document.getElementById("amount").value);

    const res = await fetch('/transfer',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({sender,receiver,amount})
    });

    const data = await res.json();
    showToast(data.message);
}

async function mine(){

    let progress = document.getElementById("progress");
    progress.style.width = "0%";

    let i = 0;
    let interval = setInterval(()=>{
        i+=10;
        progress.style.width = i + "%";
        if(i>=100) clearInterval(interval);
    },150);

    await new Promise(r=>setTimeout(r,1500));

    const res = await fetch('/mine');
    const data = await res.json();

    showToast(data.hash ? "Block mined!" : data.message);
    loadChain();
}

async function loadChain(){

    const res = await fetch('/chain');
    const data = await res.json();

    const blocksDiv = document.getElementById("blocks");
    blocksDiv.innerHTML = "";

    data.reverse().forEach(block=>{
        blocksDiv.innerHTML += `
            <div class="block-item">
                Block #${block.index} - ${block.hash.substring(0,12)}...
            </div>
        `;
    });

    updateChart(data.length);
}
async function searchAddress(){

    const address = document.getElementById("searchAddress").value;

    const res = await fetch('/address/' + address);
    const data = await res.json();

    let html = `
        <p><b>Balance:</b> ${data.balance}</p>
        <h4>Transactions:</h4>
    `;

    if(data.transactions.length === 0){
        html += "<p>No transactions found</p>";
    } else {
        data.transactions.forEach(tx=>{
            html += `
                <div style="padding:5px;margin:5px 0;background:#2b3139;border-radius:6px">
                    Block #${tx.block} — ${tx.sender} → ${tx.receiver} (${tx.amount})
                </div>
            `;
        });
    }

    document.getElementById("addressResult").innerHTML = html;
}
function updateChart(total){

    const ctx = document.getElementById("blockChart").getContext("2d");

    if(chart) chart.destroy();

    chart = new Chart(ctx,{
        type:'line',
        data:{
            labels:Array.from({length:total},(_,i)=>i),
            datasets:[{
                label:'Total Blocks',
                data:Array.from({length:total},(_,i)=>i+1),
                borderColor:'#f0b90b',
                backgroundColor:'rgba(240,185,11,0.3)',
                tension:0.4,
                fill:true
            }]
        }
    });
}

window.onload = loadChain;