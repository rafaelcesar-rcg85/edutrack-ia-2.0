query "disciplinas" verb=PATCH {
  description = "Atualiza uma disciplina existente"
  auth = "user"

  input {
    int id {
      description = "ID da disciplina a ser atualizada"
    }
    text nome? filters=trim {
      description = "Novo nome da disciplina"
    }
    int prof_id? {
      description = "Novo ID do professor"
    }
    int course_id? {
      description = "Novo ID do curso"
    }
  }

  stack {
    // Busca a disciplina garantindo que pertence ao usuário
    db.get "disciplinas" {
      where = ($db.disciplinas.id == $input.id) && ($db.disciplinas.user_id == $auth.id)
    } as $existing_disc
    
    precondition {
      if ($existing_disc == null) {
        throw "Disciplina não encontrada ou acesso negado"
      }
    }

    db.edit "disciplinas" {
      id = $input.id
      data = {
        nome      : $input.nome ?? $existing_disc.nome
        prof_id   : $input.prof_id ?? $existing_disc.prof_id
        course_id : $input.course_id ?? $existing_disc.course_id
      }
    } as $updated_disc
  }

  response = $updated_disc
}
