// =============================================================
// apis/rafaels_workspace/patch_update_theme.xs — PATCH /update_theme
// =============================================================
// Endpoint que atualiza as preferências de tema (theme_preferences)
// do próprio usuário autenticado.
//
// Método HTTP: PATCH
// Autenticação: obrigatória (token JWT)
//
// O Xano identifica o usuário pelo $auth.id extraído do JWT.
// =============================================================

query "update_theme" verb=PATCH {
  description = "Atualiza as preferências de tema (theme_preferences) do usuário autenticado."
  auth = "user"

  input {
    // Preferências de tema serializadas como texto (string JSON)
    text theme_preferences {
      description = "Dicionário do tema serializado em formato texto JSON"
    }
  }

  stack {
    // Atualiza o campo theme_preferences na tabela user do usuário logado
    db.patch "user" {
      field_name  = "id"
      field_value = $auth.id
      data = {
        theme_preferences: $input.theme_preferences
      }
    } as $updated_user
  }

  response = $updated_user
}
