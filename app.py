import streamlit as st
import oci
import json

# 1. Carrega as configurações OCI a partir dos Secrets do Streamlit
config_oci = {
    "user": st.secrets["oci"]["user"],
    "fingerprint": st.secrets["oci"]["fingerprint"],
    "key_content": st.secrets["oci"]["key_content"],
    "tenancy": st.secrets["oci"]["tenancy"],
    "region": st.secrets["oci"]["region"]
}

# 2. Inicializa o cliente do Object Storage
object_storage_client = oci.object_storage.ObjectStorageClient(config_oci)
namespace = st.secrets["oci"]["namespace"]
bucket_name = st.secrets["oci"]["bucket_name"]

st.title("🛡️ Painel de Moderação de Posts (OCI + Streamlit)")

# Exemplo: Listar objetos pendentes no Bucket
try:
    response = object_storage_client.list_objects(namespace, bucket_name)
    objetos = response.data.objects

    st.subheader("Posts Aguardando Moderação")
    
    for obj in objetos:
        if obj.name.startswith("post_"):
            # Baixa o conteúdo JSON do post do OCI
            get_obj = object_storage_client.get_object(namespace, bucket_name, obj.name)
            dados_post = json.loads(get_obj.data.content.decode('utf-8'))
            
            st.write(f"**Autor:** {dados_post.get('author')}")
            st.write(f"**Mensagem:** {dados_post.get('content')}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Aprovar", key=f"app_{obj.name}"):
                    # Lógica para mover ou atualizar status
                    st.success("Post Aprovado!")
            with col2:
                if st.button("❌ Reprovar", key=f"rep_{obj.name}"):
                    # Lógica para deletar do bucket
                    object_storage_client.delete_object(namespace, bucket_name, obj.name)
                    st.warning("Post removido do bucket!")
            st.divider()

except Exception as e:
    st.error(f"Erro ao conectar ao OCI Object Storage: {e}")