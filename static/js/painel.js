document.addEventListener("DOMContentLoaded", () => {

    const lista = document.querySelector(".conversas");
    const mensagensDiv = document.querySelector(".mensagens");
    const input = document.querySelector(".resposta input");
    const botao = document.querySelector(".resposta button");

    // 🔹 Carregar conversas
    fetch("/api/conversas")
        .then(res => res.json())
        .then(conversas => {

            lista.innerHTML = "";

            conversas.forEach(c => {
                const li = document.createElement("li");
                li.classList.add("conversa");
                li.innerHTML = `
                    <strong>${c.nome}</strong><br>
                    <span>${c.ultima_mensagem}</span>
                `;

                li.onclick = () => carregarConversa(c.id);
                lista.appendChild(li);
            });
        });

    // 🔹 Carregar mensagens
    function carregarConversa(id) {

        fetch(`/api/conversa/${id}`)
            .then(res => res.json())
            .then(data => {

                mensagensDiv.innerHTML = "";

                data.mensagens.forEach(m => {
                    const div = document.createElement("div");
                    div.classList.add("mensagem", m.remetente);
                    div.innerText = m.conteudo;
                    mensagensDiv.appendChild(div);
                });

                mensagensDiv.scrollTop = mensagensDiv.scrollHeight;
            });
    }

    // 🔹 Enviar resposta manual
    botao.onclick = () => {

        const texto = input.value.trim();
        if (!texto) return;

        fetch("/api/responder", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({mensagem: texto})
        });

        const div = document.createElement("div");
        div.classList.add("mensagem", "atendente");
        div.innerText = texto;

        mensagensDiv.appendChild(div);
        input.value = "";
        mensagensDiv.scrollTop = mensagensDiv.scrollHeight;
    };

});
