const input = document.getElementById("messageInput");
const sendBtn = document.getElementById("sendBtn");
const messages = document.getElementById("chatMessages");

sendBtn.addEventListener("click", enviar);
input.addEventListener("keypress", e => {
    if (e.key === "Enter") enviar();
});

function enviar() {
    const texto = input.value.trim();
    if (!texto) return;

    const msg = document.createElement("div");
    msg.classList.add("message", "agent");

    msg.innerHTML = `
        <span>${texto}</span>
        <div class="meta">agora</div>
    `;

    messages.appendChild(msg);
    messages.scrollTop = messages.scrollHeight;
    input.value = "";

    console.log("Mensagem enviada:", texto);
}
function adicionarMensagem(html) {
    const container = document.getElementById("chatMessages");
    container.insertAdjacentHTML("beforeend", html);

    agruparMensagens();
    container.scrollTop = container.scrollHeight;
}

