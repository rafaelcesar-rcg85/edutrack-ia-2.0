query "professores" verb=GET {
  description = "Retorna os professores, opcionalmente filtrados por curso"
  auth = "user"

  input {
    int course_id? {
      description = "ID do curso para filtrar os professores"
    }
  }

  stack {
    conditional {
      if ($input.course_id) {
        db.query "professores" {
          where = ($db.professores.user_id == $auth.id) && (($db.professores.course_id == $input.course_id) || ($db.professores.course_id == null))
          sort = {professores.created_at: "desc"}
          return = {type: "list"}
        } as $professores
      } else {
        db.query "professores" {
          where = $db.professores.user_id == $auth.id
          sort = {professores.created_at: "desc"}
          return = {type: "list"}
        } as $professores
      }
    }
  }

  response = $professores
}
