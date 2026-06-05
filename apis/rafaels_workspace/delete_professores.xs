query "professores" verb=DELETE {
  description = "Deleta um professor existente"
  auth = "user"

  input {
    int id {
      description = "ID do professor a ser deletado"
    }
  }

  stack {
    // Busca o professor garantindo que pertence ao usuário
    db.get "professores" {
      where = ($db.professores.id == $input.id) && ($db.professores.user_id == $auth.id)
    } as $existing_prof
    
    precondition {
      if ($existing_prof == null) {
        throw "Professor não encontrado ou acesso negado"
      }
    }

    db.delete "professores" {
      where = $db.professores.id == $input.id
    }
  }

  response = {
    success: true
    message: "Professor deletado com sucesso"
  }
}
