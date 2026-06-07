// Deletes a user and all related records. Requires admin authentication.
query "user/{id}" verb=DELETE {
  api_group = "admin"
  auth = "user"

  input {
    // User ID to delete
    // User ID to delete
    int id
  }

  stack {
    // Get the authenticated user to verify admin status
    db.get user {
      field_name = "id"
      field_value = $auth.id
    } as $current_user
  
    // Verify admin role
    precondition ($current_user.role == "admin") {
      error_type = "accessdenied"
      error = "Unauthorized: You do not have admin privileges."
    }
  
    // Wrap deletions in a transaction for atomicity
    db.transaction {
      stack {
        // 1. Deleta tarefas do usuário
        db.bulk.delete tarefas {
          where = $db.tarefas.user_id == $input.id
        } as $deleted_tarefas
      
        // 2. Deleta disciplinas do usuário
        db.bulk.delete disciplinas {
          where = $db.disciplinas.user_id == $input.id
        } as $deleted_disciplinas
      
        // 3. Deleta professores do usuário
        db.bulk.delete professores {
          where = $db.professores.user_id == $input.id
        } as $deleted_professores
      
        // 4. Deleta cursos do usuário (Fixed table name from 'courses' to 'curso')
        db.bulk.delete curso {
          where = $db.curso.user_id == $input.id
        } as $deleted_cursos
      
        // 5. Deleta perfil do usuário
        db.bulk.delete user_profiles {
          where = $db.user_profiles.user_id == $input.id
        } as $deleted_profiles
      
        // 6. Deleta logs de eventos do usuário
        db.bulk.delete event_log {
          where = $db.event_log.user_id == $input.id
        } as $deleted_logs
      
        // 7. Deleta o usuário principal
        db.del user {
          field_name = "id"
          field_value = $input.id
        }
      }
    }
  }

  response = {
    message: "User and all related records deleted successfully"
  }
}