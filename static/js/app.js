document.addEventListener("DOMContentLoaded", () => {

    console.log("app.js carregado");

    const input = document.getElementById("messageInput");
    const sendBtn = document.getElementById("sendBtn");
    const messages = document.getElementById("chatMessages");

    const assumeBtn = document.getElementById("assumeBtn");
    const endBtn = document.getElementById("endBtn");

    // ==========================
    // BOTÕES DE CONTROLE
    // ==========================
    assumeBtn.addEventListener("click", () => {
        ativarHumano();
    });

    endBtn.addEventListener("click", () => {
        ativarBot();
        adicionarMensagem(
            "bot",
            "🔒 Atendimento encerrado. O bot assumiu novamente."
        );
    });

    // ==========================
    // DETECÇÃO DE SCROLL
    // ==========================
    messages.addEventListener("scroll", () => {

        const margem = 40;
        const noFim =
            messages.scrollTop + messages.clientHeight >=
            messages.scrollHeight - margem;

        estadoLeitura.noFimDoChat = noFim;

        if (noFim) {
            marcarMensagensComoLidas();
        }
    });

    // ==========================
    // FUNÇÃO CENTRAL DE MENSAGEM
    // ==========================
    function adicionarMensagem(remetente, texto) {

        const msg = document.createElement("div");
        msg.classList.add("message");

        let classeHora = "read";
        let ticks = "✓✓";

        if (remetente === "usuario") {
            msg.classList.add("other");

            if (!estadoLeitura.noFimDoChat) {
                msg.classList.add("unread");
                classeHora = "unread";
                ticks = "✓";
            }
        }

        if (remetente === "bot") {
            msg.classList.add("user");
        }

        if (remetente === "atendente") {
            msg.classList.add("agent");
        }

        msg.innerHTML = `
            <div class="bubble">
                <span class="text">${texto}</span>
                <span class="time ${classeHora}">agora ${ticks}</span>
            </div>
        `;

        messages.appendChild(msg);

        agruparMensagens();

        // ❗ só faz auto-scroll se estiver no fim
        if (estadoLeitura.noFimDoChat) {
            messages.scrollTop = messages.scrollHeight;
        }
    }

    // ==========================
    // MARCAR COMO LIDAS
    // ==========================
    function marcarMensagensComoLidas() {

        const naoLidas = document.querySelectorAll(".message.other.unread");

        naoLidas.forEach(msg => {

            msg.classList.remove("unread");

            const time = msg.querySelector(".time");
            if (time) {
                time.classList.remove("unread");
                time.classList.add("read");
                time.textContent = time.textContent.replace("✓", "✓✓");
            }
        });
    }

    // ==========================
    // ENVIO ATENDENTE
    // ==========================
    function enviarMensagem() {

        if (estadoChat.modo !== "humano") return;

        const texto = input.value.trim();
        if (!texto) return;

        adicionarMensagem("atendente", texto);
        input.value = "";
    }

    sendBtn.addEventListener("click", enviarMensagem);

    input.addEventListener("keydown", (e) => {
        if (e.key === "Enter") enviarMensagem();
    });

    // ==========================
    // SIMULAÇÃO USUÁRIO (DEV)
    // ==========================
    window.simularMensagemUsuario = function (texto) {

        mostrarDigitando();

        setTimeout(() => {
            esconderDigitando();
            adicionarMensagem("usuario", texto);
        }, 1200);
    };

});
