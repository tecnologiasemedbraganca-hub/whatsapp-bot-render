document.addEventListener("DOMContentLoaded", () => {

    console.log("app.js carregado");

    const input = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendBtn");
    const messages = document.getElementById("chatMessages");

    const assumeBtn = document.getElementById("assumeBtn");
    const endBtn = document.getElementById("endBtn");

    // 🔥 VÍNCULO EXPLÍCITO DOS BOTÕES
    assumeBtn.addEventListener("click", () => {
        console.log("Assumir clicado");
        ativarHumano();
    });

    endBtn.addEventListener("click", () => {
    console.log("Encerrar clicado");

    // volta para bot
    ativarBot();

    // mensagem visual no chat
    const msg = document.createElement("div");
    msg.classList.add("message", "user");

    msg.innerHTML = `
        <div class="bubble">
            <span class="text">🔒 Atendimento encerrado. O bot assumiu novamente.</span>
            <span class="time">agora</span>
        </div>
    `;

    messages.appendChild(msg);
    agruparMensagens();
    messages.scrollTop = messages.scrollHeight;
    });
 

    // resto do código continua igual…

    // ==========================
    // ENVIO DE MENSAGEM (ATENDENTE)
    // ==========================
    function enviarMensagem() {

        // 🔒 bloqueia envio se bot estiver ativo
        if (estadoChat.modo !== "humano") {
            console.warn("Bot ativo — envio bloqueado");
            return;
        }

        const texto = input.value.trim();
        if (!texto) return;

        // cria estrutura correta
        const msg = document.createElement("div");
        msg.classList.add("message", "agent");

        msg.innerHTML = `
            <div class="bubble">
                <span class="text">${texto}</span>
                <span class="time">agora ✓✓</span>
            </div>
        `;

        messages.appendChild(msg);

        // agrupa corretamente
        agruparMensagens();

        // scroll automático
        messages.scrollTop = messages.scrollHeight;

        // limpa input
        input.value = "";

        console.log("Mensagem do atendente:", texto);

        // 🔮 FUTURO: enviar para backend / WhatsApp API
        // fetch("/api/responder", { ... })
    }

    // ==========================
    // EVENTOS
    // ==========================
    sendBtn.addEventListener("click", enviarMensagem);

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            enviarMensagem();
        }
    });

    // ==========================
    // SIMULAÇÃO BOT (DEV)
    // ==========================
    window.simularRespostaBot = function (texto) {

        mostrarDigitando();

        setTimeout(() => {

            esconderDigitando();

            const msg = document.createElement("div");
            msg.classList.add("message", "user");

            msg.innerHTML = `
                <div class="bubble">
                    <span class="text">${texto}</span>
                    <span class="time">agora ✓✓</span>
                </div>
            `;

            messages.appendChild(msg);
            agruparMensagens();
            messages.scrollTop = messages.scrollHeight;

        }, 1200);
    };

});
