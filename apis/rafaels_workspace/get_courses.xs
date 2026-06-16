// =============================================================
// apis/.../get_courses.xs — GET /curso
// =============================================================
// Endpoint que lista todos os cursos do aluno autenticado.
//
// Método HTTP: GET (somente leitura, sem corpo de requisição)
// Autenticação: obrigatória (token JWT no cabeçalho)
//
// Fluxo:
//   1. O aluno faz GET /curso com seu token JWT
//   2. O Xano valida o token e extrai $auth.id
//   3. O banco filtra apenas os cursos onde user_id = $auth.id
//   4. Retorna a lista ordenada do mais recente para o mais antigo
// =============================================================
// Declara o endpoint GET na rota "/curso"
query "curso" verb=GET {
  description = "Retorna todos os cursos pertencentes ao aluno autenticado"
  // auth = "user": apenas usuários logados podem acessar este endpoint
  // O Xano valida o token JWT e disponibiliza os dados do usuário em $auth
  auth = "user"

  // Bloco de inputs: parâmetros que o cliente pode enviar
  // Este endpoint não precisa de parâmetros — retorna todos os cursos do usuário
  input {
  }

  // Bloco stack: sequência de operações executadas no servidor
  stack {
    // db.query: consulta múltiplos registros no banco de dados
    db.query "curso" {
      // where: filtro SQL — só traz cursos onde user_id == ID do usuário logado
      // $auth.id é injetado automaticamente pelo Xano a partir do token JWT
      where = $db.curso.user_id == $auth.id
      // sort: ordena por data de criação de forma decrescente (mais recente primeiro)
      sort = {curso.created_at: "desc"}
      // return type "list": retorna um array (lista) de registros
      return = {type: "list"}
    } as $cursos  // Salva o resultado na variável $cursos
  }

  // response: define o que será retornado ao cliente
  response = $cursos
}
