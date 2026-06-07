// =============================================================
// apis/.../patch_change_email.xs — PATCH /auth/change_email
// =============================================================
// Endpoint que permite ao próprio usuário autenticado atualizar
// seu e-mail de acesso.
//
// Método HTTP: PATCH (atualização parcial)
// Autenticação: obrigatória (token JWT)
//
// Diferença importante:
//   - Este endpoint é para o PRÓPRIO usuário alterar SEU email
//   - O admin tem um endpoint separado para alterar o email de outros
//
// O Xano identifica o usuário pelo $auth.id extraído do JWT,
// sem precisar receber o user_id como parâmetro —
// isso previne que alguém tente alterar o email de outro usuário.
// =============================================================

// Permite que o próprio usuário autenticado atualize seu e-mail
query "auth/change_email" verb=PATCH {
  description = "Permite que o usuário autenticado atualize seu próprio e-mail."
  // auth = "user": apenas usuários logados podem alterar o próprio e-mail
  auth = "user"

  input {
    // Novo e-mail desejado pelo usuário
    // filters=trim: remove espaços em branco para evitar erros de formato
    text new_email filters=trim {
      description = "Novo e-mail do usuário"
    }
  }

  stack {
    // Atualiza o campo "email" diretamente na tabela "user"
    // O campo_name="id" e field_value=$auth.id garante que apenas
    // O PRÓPRIO usuário logado seja atualizado — nunca outro
    db.patch "user" {
      field_name  = "id"
      field_value = $auth.id  // ID do usuário logado, extraído do token JWT
      data = {
        email: $input.new_email
      }
    } as $updated_user
  }

  // Retorna confirmação simples de sucesso ao invés do objeto completo do usuário
  // (evita expor dados sensíveis desnecessariamente)
  response = {
    success: true,
    message: "E-mail atualizado com sucesso."
  }
}
