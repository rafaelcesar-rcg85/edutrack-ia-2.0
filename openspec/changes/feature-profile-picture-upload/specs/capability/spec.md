# feature-profile-picture-upload Specification

## Purpose
Estabelecer os requisitos para alterar a API POST /user_profiles no backend Xano, de forma que o upload de fotos de perfil seja processado nativamente pelo sistema de armazenamento (Vault) do Xano, eliminando a corrupção de imagens e permitindo a visualização correta tanto no painel web quanto no aplicativo Streamlit.

## ADDED Requirements

### Requirement: Alterar input da API para File Resource
A API POST /user_profiles SHALL receber o campo `profile_picture` como tipo File Resource (arquivo físico) em vez de tipo `image` com Base64 inline.

#### Scenario: Recebimento correto do arquivo
- **WHEN** o aplicativo Streamlit envia um arquivo de imagem via multipart/form-data
- **THEN** a API reconhece o arquivo como File Resource e o processa adequadamente

### Requirement: Processar a imagem com Create Image Metadata
O Function Stack da API POST /user_profiles SHALL incluir a função `Create Image Metadata` para converter o arquivo recebido em metadados de imagem válidos.

#### Scenario: Processamento da imagem
- **WHEN** um arquivo de imagem é enviado e chega ao Function Stack
- **THEN** a função Create Image Metadata processa o arquivo, armazena-o no Vault do Xano e gera uma variável com os metadados (incluindo URL pública)

### Requirement: Mapear metadados para coluna profile_picture
A coluna `profile_picture` na tabela `users` SHALL receber o resultado da função Create Image Metadata, e não o arquivo cru ou Base64.

#### Scenario: Armazenamento correto do metadado de imagem
- **WHEN** a função Create Image Metadata conclui o processamento com sucesso
- **THEN** a etapa Edit Record (ou Add Record) do Function Stack mapeia a variável de saída para a coluna `profile_picture`

### Requirement: Garantir retrocompatibilidade de visualização
O aplicativo Streamlit SHALL continuar conseguindo exibir imagens tanto a partir da URL do Vault (novo padrão) quanto a partir de Base64 armazenado na coluna `profile_picture_base64` (retrocompatibilidade com registros antigos).

#### Scenario: Exibição de foto antiga em Base64
- **WHEN** um usuário antigo que possui a foto em Base64 na coluna `profile_picture_base64` acessa o perfil
- **THEN** o aplicativo exibe a imagem corretamente do Base64

#### Scenario: Exibição de foto nova com URL
- **WHEN** um usuário novo faz upload de foto via File Resource
- **THEN** o aplicativo exibe a imagem usando a URL pública fornecida pelo Vault do Xano
