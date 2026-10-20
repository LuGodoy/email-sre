import streamlit as st
import json

# ==========================================
# CÓDIGO OCI COMENTADO PARA TESTES LOCAIS:
# ==========================================
# 1. Carrega as configurações OCI a partir dos Secrets do Streamlit
# config_oci = {
#     "user": st.secrets["oci"]["user"],
#     "fingerprint": st.secrets["oci"]["fingerprint"],
#     "key_content": st.secrets["oci"]["key_content"],
#     "tenancy": st.secrets["oci"]["tenancy"],
#     "region": st.secrets["oci"]["region"]
# }

# 2. Inicializa o cliente do Object Storage
# object_storage_client = oci.object_storage.ObjectStorageClient(config_oci)
# namespace = st.secrets["oci"]["namespace"]
# bucket_name = st.secrets["oci"]["bucket_name"]
# ==========================================

st.title("🛡️ Painel de Moderação de Posts (OCI + Streamlit)")

# Bloco em modo de simulação local
st.subheader("Posts Aguardando Moderação (Modo de Teste)")

# Simulando objetos que viriam do bucket
objetos_simulados = [
    {
        "name": "post_123.json",
        "author": "Luciene",
        "content": "Adorei a nova atualização do sistema, está incrível!"
    }
]

try:
    # Quando for para a nuvem, você descomenta a chamada real:
    # response = object_storage_client.list_objects(namespace, bucket_name)
    # objetos = response.data.objects
    
    for obj in objetos_simulados:
        # Baixa o conteúdo JSON do post (aqui simulado diretamente do dicionário)
        dados_post = obj
        
        st.write(f"**Autor:** {dados_post.get('author')}")
        st.write(f"**Mensagem:** {dados_post.get('content')}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Aprovar", key=f"app_{obj['name']}"):
                # Lógica para mover ou atualizar status
                st.success("Post Aprovado! (Simulação)")
        with col2:
            if st.button("❌ Reprovar", key=f"rep_{obj['name']}"):
                # Lógica para deletar do bucket
                st.warning("Post removido do bucket! (Simulação)")
        st.divider()

except Exception as e:
    st.error(f"Erro ao conectar ao OCI Object Storage: {e}")