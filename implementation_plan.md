# Refatoração do App para Arquitetura Multipage

Este plano visa dividir o arquivo único `edutrack_xano.py` em uma estrutura mais organizada, modular e expansível para o Streamlit, utilizando o sistema nativo de páginas (`st.navigation` e `st.Page`).

## Proposed Changes

A atual estrutura monolítica (onde tudo está em `edutrack_xano.py`) será refatorada. Criaremos diretórios dedicados e separaremos a lógica de API da lógica de UI.

### Utils

Extração de funções comuns para evitar repetição e facilitar testes.

#### [NEW] [api.py](file:///c:/Users/Rafael%20Impacta/Documents/edutrack-ia-2.0/utils/api.py)
- Criação deste arquivo dentro de uma nova pasta `utils/`.
- Conterá a constante `BASE_URL` e as funções `get_headers`, `api_get`, `api_post`, `api_patch` e `api_delete`.

### Pages

Criação da pasta `pages/` para armazenar as páginas da aplicação, separando responsabilidades.

#### [NEW] [login.py](file:///c:/Users/Rafael%20Impacta/Documents/edutrack-ia-2.0/pages/login.py)
- Conterá a função `tela_acesso` com lógica de login e cadastro.

#### [NEW] [dashboard.py](file:///c:/Users/Rafael%20Impacta/Documents/edutrack-ia-2.0/pages/dashboard.py)
- Conterá o painel geral (gráficos, resumos).

#### [NEW] [professores.py](file:///c:/Users/Rafael%20Impacta/Documents/edutrack-ia-2.0/pages/professores.py)
- Conterá o CRUD de professores.

#### [NEW] [disciplinas.py](file:///c:/Users/Rafael%20Impacta/Documents/edutrack-ia-2.0/pages/disciplinas.py)
- Conterá o CRUD de disciplinas.

#### [NEW] [tarefas.py](file:///c:/Users/Rafael%20Impacta/Documents/edutrack-ia-2.0/pages/tarefas.py)
- Conterá o CRUD de tarefas e notas.

### Entry Point

O arquivo principal atuará como roteador, controlando o fluxo baseado no estado da autenticação (`st.session_state.logged_in`).

#### [MODIFY] [edutrack_xano.py](file:///c:/Users/Rafael%20Impacta/Documents/edutrack-ia-2.0/edutrack_xano.py)
- Removerá todo o código das telas e APIs.
- Manterá a inicialização do estado de sessão.
- Definirá os `st.Page` e a navegação usando `st.navigation()`. 
- Adicionará o botão de "Sair" na sidebar de forma global ou acoplada ao sistema de navegação.

## Verification Plan

### Manual Verification
- O usuário deverá acessar o app usando o comando já em execução e verificar se a tela de login aparece.
- O usuário fará login e navegará entre as diferentes páginas na barra lateral (Painel, Professores, Disciplinas, Tarefas).
- Realizar operações CRUD em cada página para garantir que as importações da API `utils/api.py` funcionam.

## User Review Required

> [!IMPORTANT]
> - Utilizarei a função `st.navigation` do Streamlit, que é o padrão recomendado e mais robusto em versões recentes, pois permite o bloqueio dinâmico das páginas para usuários que não estejam logados. Isso requer Streamlit 1.36+ (nós verificamos que você tem a 1.56.0 instalada, então está perfeito).
> - Por favor, revise o plano. Se você aprovar, começarei a refatoração imediatamente.
