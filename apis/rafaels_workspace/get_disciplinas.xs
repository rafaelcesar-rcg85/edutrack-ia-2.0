query "disciplinas" verb=GET {
  description = "Retorna as disciplinas, opcionalmente filtradas por curso"
  auth = "user"

  input {
    int course_id? {
      description = "ID do curso para filtrar as disciplinas"
    }
  }

  stack {
    conditional {
      if ($input.course_id) {
        db.query "disciplinas" {
          where = ($db.disciplinas.user_id == $auth.id) && (($db.disciplinas.course_id == $input.course_id) || ($db.disciplinas.course_id == null))
          sort = {disciplinas.created_at: "desc"}
          return = {type: "list"}
        } as $disciplinas
      } else {
        db.query "disciplinas" {
          where = $db.disciplinas.user_id == $auth.id
          sort = {disciplinas.created_at: "desc"}
          return = {type: "list"}
        } as $disciplinas
      }
    }
  }

  response = $disciplinas
}
