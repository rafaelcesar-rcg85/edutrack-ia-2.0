# Tasks: feature-profile-picture-upload

## Escopo
Modificação da API POST /user_profiles no backend Xano para processar corretamente o upload de fotos de perfil utilizando o sistema nativo de armazenamento (Vault) do Xano.

---

## Tasks

### 1. Abrir a API POST /user_profiles no Xano
- [ ] Faça login no painel web do Xano
- [ ] Navegue para **API** (seção de APIs)
- [ ] Localize e abra a API chamada **POST /user_profiles**

### 2. Remover o input atual de profile_picture
- [ ] Na seção **Inputs** (azul), localize o campo `profile_picture` (que deve estar com tipo `image`)
- [ ] Clique no ícone de lixeira para deletar esse input

### 3. Criar novo input para profile_picture como File Resource
- [ ] Ainda na seção **Inputs**, clique em **+ Add Input**
- [ ] Escolha o tipo de storage: **File Resource** (ou pesquise por "File Resource" se não aparecer diretamente)
- [ ] Nomeie o input exatamente como `profile_picture`
- [ ] Clique em confirmar/criar

### 4. Adicionar função Create Image Metadata no Function Stack
- [ ] Abra a seção **Function Stack** (verde)
- [ ] Clique em **+ Add Function**
- [ ] Navegue para: **Content Upload** → **Create Image Metadata**
- [ ] Na configuração da função:
  - Selecione o **file input** como `profile_picture` (o que você acabou de criar)
  - Deixe a **variável de saída** com o nome padrão (geralmente `image_metadata` ou `var_1`)

### 5. Mapear a saída para a coluna profile_picture
- [ ] Ainda no **Function Stack**, localize a função que salva no banco (**Edit Record** ou **Add Record**)
- [ ] Abra essa função clicando nela
- [ ] Procure pela coluna `profile_picture` no mapeamento de dados
- [ ] Mude o valor dessa coluna de `input.profile_picture` para a variável de saída da função **Create Image Metadata** (ex: `image_metadata` ou `var_1`)
- [ ] Confirme as alterações na função

### 6. Publicar as mudanças
- [ ] Volte para a tela principal da API POST /user_profiles
- [ ] Clique em **Publish** (botão no topo da tela)
- [ ] Aguarde a publicação ser concluída

### 7. Testar o upload via aplicativo Streamlit
- [ ] Abra o aplicativo Streamlit (edutrak_xano.py)
- [ ] Navegue até a página **Meu Perfil**
- [ ] Faça upload de uma foto e clique em "Salvar Perfil"
- [ ] Verifique se a mensagem de sucesso aparece
- [ ] Abra o painel do Xano e verifique se a foto aparece corretamente (sem o ícone quebrado) na tabela `users`

---

## Notas
- Nenhum código Python precisa ser alterado. O arquivo `profile.py` já está configurado para enviar o arquivo no formato correto.
- A retrocompatibilidade com fotos antigas em Base64 é mantida automaticamente pelo aplicativo Streamlit.
