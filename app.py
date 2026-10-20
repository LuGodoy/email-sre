import json
import os
import streamlit as st

POSTS_PENDENTES = os.path.join(os.path.dirname(__file__), "data", "posts_pendentes.json")
POSTS_APROVADOS = os.path.join(os.path.dirname(__file__), "data", "posts_aprovados.json")


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
    if post:
        post["status"] = "aprovado"
        aprovados.append(post)
        salvar(POSTS_APROVADOS, aprovados)
        salvar(POSTS_PENDENTES, [p for p in pendentes if p["id"] != post_id])
        st.rerun()


def reprovar(post_id: str) -> None:
    pendentes = carregar(POSTS_PENDENTES)
    salvar(POSTS_PENDENTES, [p for p in pendentes if p["id"] != post_id])
    st.rerun()


st.title("🛡️ Painel de Moderação de Posts")

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
