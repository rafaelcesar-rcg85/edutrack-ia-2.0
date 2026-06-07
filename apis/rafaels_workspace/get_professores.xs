// =============================================================
// apis/.../get_professores.xs — GET /professores
// =============================================================
// Endpoint que lista os professores do aluno, com filtro opcional por curso.
//
// Método HTTP: GET (leitura)
// Autenticação: obrigatória (token JWT)
//
// Parâmetro opcional: course_id
//   - Se fornecido → retorna professores do curso E os sem curso (globais)
//   - Se omitido   → retorna TODOS os professores do usuário
//
// Padrão idêntico ao get_disciplinas — permite filtrar
// os professores ao selecionar um curso na interface.
// =============================================================

// Lista os professores, opcionalmente filtrados por curso
query "professores" verb=GET {
  description = "Retorna os professores, opcionalmente filtrados por curso"
  auth = "user"

  input {
    // course_id é opcional (?) — filtro aplicado apenas se enviado
    int course_id? {
      description = "ID do curso para filtrar os professores"
    }
  }

  stack {
    // Bloco condicional: escolhe qual consulta executar
    conditional {
      // Caso 1: filtro por curso foi informado
      if ($input.course_id) {
        db.query "professores" {
          // Traz professores que:
          //   - pertencem ao usuário logado
          //   - E que estão no curso informado OU não têm curso definido (globais)
          where = ($db.professores.user_id == $auth.id) && (($db.professores.course_id == $input.course_id) || ($db.professores.course_id == null))
          sort  = {professores.created_at: "desc"}
          return = {type: "list"}
        } as $professores
      } else {
        // Caso 2: sem filtro → retorna todos os professores do usuário
        db.query "professores" {
          where  = $db.professores.user_id == $auth.id
          sort   = {professores.created_at: "desc"}
          return = {type: "list"}
        } as $professores
      }
    }
  }

  // Retorna a lista de professores (filtrada ou completa)
  response = $professores
}
