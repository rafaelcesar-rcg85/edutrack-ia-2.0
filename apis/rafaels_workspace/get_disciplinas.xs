// =============================================================
// apis/.../get_disciplinas.xs — GET /disciplinas
// =============================================================
// Endpoint que lista as disciplinas do aluno, com filtro opcional por curso.
//
// Método HTTP: GET (leitura)
// Autenticação: obrigatória (token JWT)
//
// Parâmetro opcional: course_id
//   - Se fornecido → retorna disciplinas do curso E as sem curso (globais)
//   - Se omitido   → retorna TODAS as disciplinas do usuário
//
// Isso permite que a tela de disciplinas filtre pelo curso selecionado.
// =============================================================

// Lista as disciplinas, opcionalmente filtradas por curso
query "disciplinas" verb=GET {
  description = "Retorna as disciplinas, opcionalmente filtradas por curso"
  auth = "user"

  input {
    // course_id é opcional (?) — o cliente pode ou não enviar este filtro
    int course_id? {
      description = "ID do curso para filtrar as disciplinas"
    }
  }

  stack {
    // Bloco condicional: executa uma consulta diferente dependendo do filtro
    conditional {
      // Caso 1: course_id foi fornecido
      if ($input.course_id) {
        db.query "disciplinas" {
          // Traz disciplinas que:
          //   - pertencem ao usuário logado  ($db.disciplinas.user_id == $auth.id)
          //   - E que OU pertencem ao curso informado OU não têm curso (null = disciplina global)
          // O operador && significa "E", o || significa "OU"
          where = ($db.disciplinas.user_id == $auth.id) && (($db.disciplinas.course_id == $input.course_id) || ($db.disciplinas.course_id == null))
          // Ordena da mais recente para a mais antiga
          sort  = {disciplinas.created_at: "desc"}
          return = {type: "list"}
        } as $disciplinas
      } else {
        // Caso 2: nenhum filtro → retorna todas as disciplinas do usuário
        db.query "disciplinas" {
          where  = $db.disciplinas.user_id == $auth.id
          sort   = {disciplinas.created_at: "desc"}
          return = {type: "list"}
        } as $disciplinas
      }
    }
  }

  // Retorna a lista de disciplinas (filtrada ou completa)
  response = $disciplinas
}
