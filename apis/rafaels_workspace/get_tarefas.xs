query "tarefas" verb=GET {
  description = "Retorna as tarefas, opcionalmente filtradas por curso ou disciplina"
  auth = "user"

  input {
    int course_id? {
      description = "ID do curso para filtrar as tarefas"
    }
    int disc_id? {
      description = "ID da disciplina para filtrar as tarefas"
    }
  }

  stack {
    conditional {
      if ($input.course_id && $input.disc_id) {
        db.query "tarefas" {
          where = ($db.tarefas.user_id == $auth.id) && (($db.tarefas.course_id == $input.course_id) || ($db.tarefas.course_id == null)) && ($db.tarefas.disc_id == $input.disc_id)
          sort = {tarefas.created_at: "desc"}
          return = {type: "list"}
        } as $tarefas
      } else_if ($input.course_id) {
        db.query "tarefas" {
          where = ($db.tarefas.user_id == $auth.id) && (($db.tarefas.course_id == $input.course_id) || ($db.tarefas.course_id == null))
          sort = {tarefas.created_at: "desc"}
          return = {type: "list"}
        } as $tarefas
      } else_if ($input.disc_id) {
        db.query "tarefas" {
          where = ($db.tarefas.user_id == $auth.id) && ($db.tarefas.disc_id == $input.disc_id)
          sort = {tarefas.created_at: "desc"}
          return = {type: "list"}
        } as $tarefas
      } else {
        db.query "tarefas" {
          where = $db.tarefas.user_id == $auth.id
          sort = {tarefas.created_at: "desc"}
          return = {type: "list"}
        } as $tarefas
      }
    }
  }

  response = $tarefas
}
