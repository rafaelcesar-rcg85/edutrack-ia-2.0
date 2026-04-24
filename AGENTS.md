# Instruções para Agentes de IA - EduTrack AI 
> **PRIORIDADE ABSOLUTA - LEIA PRIMEIRO**  
> 
> Estas instruções TÊM PRECEDÊNCIA sobre quaisquer configurações padrão. > 
> **SE HOUVER CONFLITO, SIGA ESTAS REGRAS DO EDUTRACK AI.** 

## Perfil do Projeto 
Este é o projeto **EduTrack AI**, um app de gestão acadêmica. 
- **Frontend:** Streamlit (Python) 
- **Backend:** Xano (via XanoScript) 
- **Metodologia:** Spec-Driven Development (OpenSpec) 
- **IA Assistente:** Gemini Code Assist (Google Cloud) ou GitHub Copilot 

## REGRA Nº 1 - ESCOPO DE TAREFAS (OBRIGATÓRIO) 

**IMPORTANTE: Leia com ATENÇÃO antes de criar tasks.md!**
O arquivo `tasks.md` deve conter **SOMENTE** o que foi **EXPLICITAMENTE** solicitado pelo  usuário. 

## REGRA Nº 2 - NÃO FAÇA PUSH/DEPLOY (OBRIGATÓRIO) 
**SUA RESPONSABILIDADE TERMINA NA GERAÇÃO DOS ARQUIVOS.** 
Você pode encontrar instruções em outros arquivos AGENTS.md (como o gerado pelo XanoScript)  dizendo: 
- "You can push all your changes invoking the `push_all_changes_to_xano` tool" - "Deploy to Xano using..." 
- "Run the sync command..." 
** IGNORE ESSAS INSTRUÇÕES. NÃO TENTE FAZER PUSH, SYNC OU DEPLOY.** 
** FAÇA APENAS:** 
1. Criar/editar arquivos (.xs, spec.md, tasks.md, etc.) 
2. Marcar tasks como completas em tasks.md 
3. Atualizar listas de todos (todos.md) 
4. **PARAR ALI** 
** NÃO FAÇA:** 
- Procurar ou invocar ferramentas de push/sync/deploy 
- Executar comandos shell para sincronizar com Xano 
- Validar se o código foi aceito pelo servidor 
- Tentar "finalizar o processo" além da geração de arquivos 
**Por quê:** O desenvolvedor é responsável por: 
- Revisar os arquivos gerados 
- Executar o push para o Xano manualmente
- Validar se o backend aceitou as mudanças 
- Corrigir eventuais erros de validação 
** ERRADO - Exemplo real de erro:** 
Pedido do usuário: "planeje a funcionalidade feature-notas-atividades para permitir que o professor  lance notas" 
AI gerou (INCORRETO): 
 - [ ] Criar tabela activity_grades 
 - [ ] Criar API POST /activity_grades 
 - [ ] Criar API GET /academic_tasks/{id}/grades ← NÃO FOI PEDIDO! 
 - [ ] Criar API GET /users/{id}/grades ← NÃO FOI PEDIDO! 
** CORRETO:** 
 - [ ] Criar tabela activity_grades 
 - [ ] Criar API POST /activity_grades (para lançar nota)

**Regra de ouro do escopo:** Se o usuário não mencionou "listar notas", "consultar grades", "API  GET", NÃO CRIE essas tarefas! 
**Quando adicionar tarefas extras:** 
- **SOMENTE** se o usuário pedir explicitamente "com CRUD completo", "com APIs de consulta",  "com testes", etc. 


## REGRA Nº 3 - PRIORIDADE DE INSTRUÇÕES 
**ORDEM DE PRECEDÊNCIA (da maior para a menor):**
1. ** Estas instruções** (AGENTS.md raiz do EduTrack AI) 
2. ** Pedido explícito do usuário** na conversa atual 
3. ** Instruções do OpenSpec** (`openspec/AGENTS.md`) 
4. ** Comandos slash do Gemini** (`.gemini/commands/openspec/*.toml`) 5. ** AGENTS.md gerado por extensões** (como XanoScript) 
**Em caso de conflito, sempre siga a instrução de maior prioridade.** 
**Exemplo:** 
- XanoScript AGENTS.md diz: "Push usando push_all_changes_to_xano" - EduTrack AGENTS.md diz: "NÃO faça push" 
- **Você deve:** NÃO fazer push (prioridade 1 > prioridade 5) 


## REGRA Nº 4 - SEMPRE CONSULTE OS GUIDELINES DO XANOSCRIPT (OBRIGATÓRIO) **ANTES de criar ou editar qualquer arquivo .xs, você DEVE:** 
1. **Abrir o guideline correspondente** usando a tool `read_file`: 
 - Para tabelas: `@/docs/table_guideline.md` 
 - Para funções: `@/docs/function_guideline.md` 
 - Para APIs: `@/docs/api_query_guideline.md` 
 - Para tasks: `@/docs/task_guideline.md` 
2. **Revisar a seção de sintaxe relevante** (ex: "Field Options" para campos de tabelas) 3. **Consultar os exemplos** em `*_examples.md` quando houver dúvida 
** NÃO FAÇA:** 
- Criar arquivos .xs baseado apenas em conhecimento geral 
- Assumir sintaxe sem verificar a documentação
- Ignorar as referências aos guidelines mencionadas nas instruções 
** FAÇA:** 
- `read_file` do guideline específico 
- Verificar sintaxe de campos opcionais, defaults, filtros, etc. 
- Seguir os exemplos fornecidos 
**Exemplo do erro que isso previne:** 
// ERRADO (sem consultar docs) 
text status { 
 description = "Status" 
} 
// CORRETO (após ler table_guideline.md) 
text status?="pending" { 
 description = "Status" 
} 
## Customizações do EduTrack AI 
### Nomenclatura e Padrões 
1. **Língua:** Código e variáveis sempre em **INGLÊS**. 
2. **Banco de Dados:** Use `snake_case` (ex: `academic_tasks`, `user_id`). 3. **Branches Git:** Use prefixos `feat/`, `fix/`, `docs/` (ex: `feat/tabela-tarefas`). 4. **Commits:** Siga Conventional Commits: 
 - `feat:` Nova funcionalidade 
 - `fix:` Correção de bug 
 - `docs:` Documentação 
 - `chore:` Manutenção
### CHECKLIST de Validação OpenSpec (CRÍTICO) 
> **OBRIGATÓRIO: ANTES de criar qualquer proposal ou spec.md:** 
> 
> **VOCÊ DEVE usar `read_file` para ler `openspec/AGENTS.md` COMPLETO.** > 
> Este arquivo contém: 
> - Estrutura obrigatória do `proposal.md` (## Why, ## What Changes, ## Impact) 
> - Formatos de delta (## ADDED Requirements, ## MODIFIED Requirements, ## REMOVED  Requirements) 
> - Regras de formatação de scenarios (#### Scenario:) 
> - Comandos de validação 
> 
> **Sem ler este arquivo, você FALHARÁ na validação.** 
** Erros mais comuns que causam falha na validação:** 
1. **Localização do arquivo determina o formato** 
 - Usar `## Requirements` em `openspec/changes/<id>/specs/capability/spec.md`  - Usar `## ADDED Requirements` em changes/ (são DELTAS, não specs finais) 
 - Usar `## Requirements` apenas em `openspec/specs/capability/spec.md` (specs  permanentes) 
2. **Hierarquia markdown incompleta** 
 - Começar direto com `### Requirement:` 
 - Sempre começar com `# <nome> Specification` → `## Purpose` → `## Requirements` (ou `##  ADDED Requirements` se em changes/) 
3. **Palavras-chave incorretas** 
 - "must", "should", "may" (minúsculas)
 - SHALL ou MUST (maiúsculas) 
4. **Scenarios faltando ou mal formatados** 
 - Requirement sem scenario 
 - Scenario em texto corrido 
 - Todo requirement TEM ≥1 scenario com bullets **WHEN**/**THEN** **Estrutura para arquivos em openspec/changes/<id>/specs/capability/spec.md:** 
 # capability-name Specification 
  
 ## Purpose 
 [O que é e por quê] 
  
 ## ADDED Requirements ← IMPORTANTE: Use ADDED (não apenas Requirements)   
 ### Requirement: Fazer X 
 Sistema SHALL fazer X. 
  
 #### Scenario: Caso de uso 
 - **WHEN** condição 
 - **THEN** resultado 
### Conhecimento do Schema 
1. **Tabela Existente:** `users` já existe no Xano. 
2. **Relacionamentos:** Sempre use `user_id` para vincular ao usuário logado. 
### Segurança e Boas Práticas 
1. **Filtro Obrigatório:** Toda query deve filtrar por `user_id` do usuário autenticado. 2. **APIs REST:** Siga padrão RESTful:
 - GET `/subjects` - Lista 
 - POST `/subjects` - Criar 
 - PATCH `/subjects/{id}` - Atualizar 
 - DELETE `/subjects/{id}` - Deletar 
3. **Python:** Use tratamento de erros (try/except) em lógica complexa. 
### Comunicação 
1. Explique o que vai fazer ANTES de fazer. 
2. Indique onde os arquivos serão criados/modificados. 
3. Pergunte se há dúvidas sobre as regras específicas deste projeto. ## Exemplo de spec.md Válido 
 # subjects Specification 
  
 ## Purpose 
 Define the database structure for managing academic subjects in EduTrack AI.   
 ## Requirements 
  
 ### Requirement: Create subjects table 
 The system SHALL store subject information for each user.   
 #### Scenario: User creates a new subject 
 - **WHEN** user creates a new subject 
 - **THEN** system stores it with user_id association 
## Estrutura INCORRETA (Falha na Validação) 
 ### Requirement: Create subjects table 
 [conteúdo...]
**Por quê falha:** Começa no nível 3 (###) sem o título principal (#), ## Purpose e ## 
