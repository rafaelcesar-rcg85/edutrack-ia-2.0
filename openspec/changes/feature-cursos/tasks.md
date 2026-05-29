# Passo a Passo no Painel do Xano (feature-cursos)

Siga estas etapas para adequar seu backend do Xano à nova estrutura de cursos:

## 1. Criar a tabela `courses`
- Vá em **Database** e clique em **Add Table**
- Nome: `courses`
- Adicione as colunas:
  - `user_id` (Table Reference -> users)
  - `name` (Text)

## 2. Gerar as APIs para `courses`
- Vá em **API** -> **Add API Endpoint**
- Crie um CRUD básico (GET, POST, PATCH, DELETE) apontando para a tabela `courses`.
- **Importante:** Em todos os endpoints, lembre-se de configurar o filtro/auth para garantir que o usuário só veja os seus próprios cursos (`courses.user_id = auth.id`).

## 3. Atualizar a tabela `disciplinas`
- Volte em **Database** e abra a tabela `disciplinas`.
- Clique em **+** para adicionar uma nova coluna.
- Escolha **Table Reference** e selecione a tabela `courses`.
- Nome da coluna: `course_id`.

## 4. Atualizar as APIs de `disciplinas`
- Vá na API `POST /disciplinas`. Adicione `course_id` (integer) nos Inputs e mapeie ele na função Add Record.
- Vá na API `GET /disciplinas`. Na Query (Query All Records), adicione um filtro: `disciplinas.course_id = input.course_id` para que a API retorne apenas as matérias do curso ativo. Lembre-se de adicionar `course_id` nos Inputs dessa API GET também.
