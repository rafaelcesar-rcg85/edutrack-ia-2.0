# Change: feature-profile-picture-upload

## Why
O upload de fotos de perfil no EduTrack AI estava funcionando, porém a imagem chegava "quebrada" ou truncada quando visualizada no painel do Xano. Isso ocorre porque a API POST /user_profiles estava tentando armazenar a imagem em Base64 diretamente numa coluna do tipo `image`, sem processar o arquivo através do sistema nativo de armazenamento (Vault) do Xano. É necessário alterar o endpoint para receber o arquivo físico via File Resource e processá-lo com a função Create Image Metadata, garantindo que a imagem seja armazenada corretamente no Vault do Xano e disponibilizada com uma URL pública válida.

## What Changes
Modificação da API POST /user_profiles para:
1. Alterar o input `profile_picture` de tipo `image` para tipo `File Resource`
2. Adicionar a função `Create Image Metadata` no Function Stack para processar o arquivo
3. Mapear a saída da função para a coluna `profile_picture` na tabela `users`

## Impact
O upload de fotos de perfil passará a funcionar nativamente, armazenando a imagem no Vault do Xano e gerando uma URL pública válida. A imagem não aparecerá mais "quebrada" no painel do Xano, e tanto o aplicativo Streamlit quanto o painel web conseguirão renderizá-la perfeitamente.
