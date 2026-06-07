// =============================================================
// apis/.../get_tarefas.xs — GET /tarefas
// =============================================================
// Endpoint mais flexível do sistema — lista tarefas com até
// dois filtros combinados opcionalmente.
//
// Método HTTP: GET (leitura)
// Autenticação: obrigatória (token JWT)
//
// Parâmetros opcionais: course_id e disc_id
// Combinações possíveis:
//   - course_id + disc_id → filtra pelo curso E pela disciplina
//   - apenas course_id   → filtra só pelo curso
//   - apenas disc_id     → filtra só pela disciplina
//   - nenhum             → retorna todas as tarefas do usuário
//
// Isso dá flexibilidade máxima para a interface filtrar os dados.
// =============================================================

// Lista as tarefas, opcionalmente filtradas por curso ou disciplina
query "tarefas" verb=GET {
  description = "Retorna as tarefas, opcionalmente filtradas por curso ou disciplina"
  auth = "user"

  input {
    // Filtros opcionais — o cliente pode enviar um, ambos ou nenhum
    int course_id? {
      description = "ID do curso para filtrar as tarefas"
    }
    int disc_id? {
      description = "ID da disciplina para filtrar as tarefas"
    }
  }

  stack {
    // Bloco condicional com 4 ramos para cobrir todas as combinações
    conditional {
      // Caso 1: AMBOS os filtros foram fornecidos (curso + disciplina)
      if ($input.course_id && $input.disc_id) {
        db.query "tarefas" {
          // Filtra por: usuário logado + (curso informado OU sem curso) + disciplina informada
          where = ($db.tarefas.user_id == $auth.id) && (($db.tarefas.course_id == $input.course_id) || ($db.tarefas.course_id == null)) && ($db.tarefas.disc_id == $input.disc_id)
          sort  = {tarefas.created_at: "desc"}
          return = {type: "list"}
        } as $tarefas

      // Caso 2: Apenas course_id foi fornecido
      } else_if ($input.course_id) {
        db.query "tarefas" {
          // Traz tarefas do curso informado OU sem curso (globais)
          where = ($db.tarefas.user_id == $auth.id) && (($db.tarefas.course_id == $input.course_id) || ($db.tarefas.course_id == null))
          sort  = {tarefas.created_at: "desc"}
          return = {type: "list"}
        } as $tarefas

      // Caso 3: Apenas disc_id foi fornecido
      } else_if ($input.disc_id) {
        db.query "tarefas" {
          // Traz tarefas do usuário na disciplina específica
          where = ($db.tarefas.user_id == $auth.id) && ($db.tarefas.disc_id == $input.disc_id)
          sort  = {tarefas.created_at: "desc"}
          return = {type: "list"}
        } as $tarefas

      } else {
        // Caso 4: Sem filtros → retorna TODAS as tarefas do usuário
        db.query "tarefas" {
          where  = $db.tarefas.user_id == $auth.id
          sort   = {tarefas.created_at: "desc"}
          return = {type: "list"}
        } as $tarefas
      }
    }
  }

  // Retorna a lista de tarefas (no cenário que se aplicou)
  response = $tarefas
}
