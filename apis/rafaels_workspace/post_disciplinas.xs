query "disciplinas" verb=POST {
  description = "Cria uma nova disciplina vinculada a um professor e um curso"
  auth = "user"

  input {
    text nome filters=trim {
      description = "Nome da disciplina"
    }
    int prof_id {
      description = "ID do professor responsável"
    }
    int course_id {
      description = "ID do curso"
    }
  }

  stack {
    db.add "disciplinas" {
      data = {
        user_id   : $auth.id
        course_id : $input.course_id
        prof_id   : $input.prof_id
        nome      : $input.nome
        created_at: "now"
      }
    } as $new_disc
  }

  response = $new_disc
}
