// =============================================================
// apis/.../patch_change_password.xs — PATCH /auth/change_password
// =============================================================
// Endpoint que permite ao próprio usuário autenticado trocar sua senha.
//
// Método HTTP: PATCH (atualização parcial)
// Autenticação: obrigatória (token JWT)
//
// Segurança:
//   - O Xano automaticamente faz o hash (criptografia) da nova senha
//   - A identificação do usuário é feita pelo $auth.id do token JWT
//   - A validação da senha ATUAL é feita no frontend (api_user_change_password)
//     antes de chamar este endpoint
//
// Nota: O tipo "password" no input instrui o Xano a tratar o
// campo como dado sensível (hash automático antes de salvar).
// =============================================================

// Permite que o próprio usuário autenticado troque sua senha
query "auth/change_password" verb=PATCH {
  description = "Permite que o usuário autenticado troque sua própria senha."
  // auth = "user": exige token JWT — apenas o próprio usuário logado pode chamar
  auth = "user"

  input {
    // Nova senha desejada
    // Tipo "password": o Xano aplica hash (bcrypt) automaticamente antes de salvar
    // Isso garante que a senha nunca seja armazenada em texto puro no banco
    password new_password {
      description = "Nova senha desejada"
    }
  }

  stack {
    // Atualiza o campo "password" na tabela "user" do usuário logado
    // Usa $auth.id para garantir que apenas o PRÓPRIO usuário seja atualizado
    db.patch "user" {
      field_name  = "id"
      field_value = $auth.id  // ID extraído automaticamente do token JWT
      data = {
        password: $input.new_password  // Será salvo como hash pelo Xano
      }
    } as $updated_user
  }

  // Retorna confirmação sem expor dados do usuário
  response = {
    success: true,
    message: "Senha alterada com sucesso."
  }
}
