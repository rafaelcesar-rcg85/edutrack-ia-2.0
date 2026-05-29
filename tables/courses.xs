table courses {
  auth = false

  schema {
    // Identificador único do curso
    int id
  
    // Aluno proprietário do curso
    int user_id {
      table = "user"
    }
  
    // Nome do curso ou instituição
    text name filters=trim
  
    // Data de criação do registro
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "user_id"}]}
  ]
}