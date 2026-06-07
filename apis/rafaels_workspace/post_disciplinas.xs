// =============================================================
// apis/.../post_disciplinas.xs — POST /disciplinas
// =============================================================
// Endpoint que cria uma nova disciplina para o aluno autenticado.
//
// Método HTTP: POST (criação)
// Autenticação: obrigatória (token JWT)
//
// Uma disciplina exige:
//   - nome: nome da disciplina
//   - prof_id: qual professor ministra
//   - course_id: a qual curso pertence
//
// O vínculo com o usuário (user_id) é feito automaticamente
// pelo Xano usando $auth.id do token JWT.
// =============================================================

// Cria uma nova disciplina vinculada a um professor e um curso
query "disciplinas" verb=POST {
  description = "Cria uma nova disciplina vinculada a um professor e um curso"
  auth = "user"

  input {
    // Nome da disciplina — obrigatório
    // filters=trim: remove espaços extras automaticamente
    text nome filters=trim {
      description = "Nome da disciplina"
    }
    // ID do professor responsável — o professor já deve estar cadastrado
    int prof_id {
      description = "ID do professor responsável"
    }
    // ID do curso ao qual a disciplina pertence
    int course_id {
      description = "ID do curso"
    }
  }

  stack {
    // db.add: insere o novo registro na tabela "disciplinas"
    db.add "disciplinas" {
      data = {
        // $auth.id: ID do usuário logado, obtido automaticamente do token JWT
        user_id   : $auth.id
        course_id : $input.course_id
        prof_id   : $input.prof_id
        nome      : $input.nome
        // "now": expressão Xano que registra o timestamp atual
        created_at: "now"
      }
    } as $new_disc  // Variável com o registro criado
  }

  // Retorna a nova disciplina criada (com o ID gerado pelo banco)
  response = $new_disc
}
