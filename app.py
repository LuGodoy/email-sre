import json
import os
import streamlit as st

POSTS_PENDENTES = os.path.join(os.path.dirname(__file__), "data", "posts_pendentes.json")
POSTS_APROVADOS = os.path.join(os.path.dirname(__file__), "data", "posts_moderados.json")


def carregar(caminho: str) -> list:
    if os.path.exists(caminho):
        with open(caminho, encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def salvar(caminho: str, dados: list) -> None:
    with open(caminho, "w", encoding="utf-8") as f:
        json.dump(dados, f, ensure_ascii=False, indent=2)


def aprovar(post_id: str) -> None:
    pendentes = carregar(POSTS_PENDENTES)
    aprovados = carregar(POSTS_APROVADOS)

    post = next((p for p in pendentes if p["id"] == post_id), None)
    if not post:
        return

    post["status"] = "aprovado"
    aprovados.append(post)
    novos_pendentes = [p for p in pendentes if p["id"] != post_id]

    salvar(POSTS_APROVADOS, aprovados)
    salvar(POSTS_PENDENTES, novos_pendentes)
    st.session_state["rerun"] = True


def reprovar(post_id: str) -> None:
    pendentes = carregar(POSTS_PENDENTES)
    post = next((p for p in pendentes if p["id"] == post_id), None)
    if not post:
        return
    post["status"] = "reprovado"
    salvar(POSTS_PENDENTES, [p for p in pendentes if p["id"] != post_id])
    aprovados = carregar(POSTS_APROVADOS)
    aprovados.append(post)
    salvar(POSTS_APROVADOS, aprovados)
    st.session_state["rerun"] = True


st.title("🛡️ Painel de Moderação de Posts")

if st.session_state.pop("rerun", False):
    st.rerun()

col_titulo, col_btn = st.columns([4, 1])
with col_btn:
    if st.button("🔄 Atualizar"):
        st.rerun()

pendentes = carregar(POSTS_PENDENTES)

if not pendentes:
    st.info("Nenhum post aguardando moderação.")
else:
    st.subheader(f"Posts Aguardando Moderação ({len(pendentes)})")

    for post in pendentes:
        with st.container(border=True):
            st.markdown(f"**{post.get('titulo', 'Sem título')}**")
            st.caption(f"✍️ {post.get('autor')} · {post.get('canal')} · {post.get('criado_em', '')[:19].replace('T', ' ')} UTC")

            with st.expander("💬 Mensagem original"):
                st.write(post.get("mensagem_original", ""))

            st.write(post.get("post", ""))

            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Aprovar", key=f"apr_{post['id']}"):
                    aprovar(post["id"])
            with col2:
                if st.button("❌ Reprovar", key=f"rep_{post['id']}"):
                    reprovar(post["id"])

# Histórico de posts moderados
historico = carregar(POSTS_APROVADOS)
if historico:
    st.divider()
    st.subheader(f"Histórico de Moderação ({len(historico)})")
    for post in reversed(historico):
        status = post.get("status", "")
        icone = "✅" if status == "aprovado" else "❌"
        label = "Aprovado" if status == "aprovado" else "Reprovado"
        cor = "green" if status == "aprovado" else "red"
        with st.expander(f"{icone} {post.get('titulo', 'Sem título')} — :{cor}[{label}]"):
            st.caption(f"✍️ {post.get('autor')} · {post.get('canal')} · {post.get('criado_em', '')[:19].replace('T', ' ')} UTC")
            st.write(post.get("post", ""))
            with st.expander("💬 Mensagem original"):
                st.write(post.get("mensagem_original", ""))
