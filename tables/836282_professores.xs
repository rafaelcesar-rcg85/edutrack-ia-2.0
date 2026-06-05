table professores {
  auth = false

  schema {
    // Identificador único do professor
    int id
  
    // Nome do professor
    text nome
  
    // E-mail de contato do professor
    email email?
  
    // ID do curso ao qual o professor pertence
    int course_id? {
      table = "courses"
    }
  
    // ID do usuário (aluno) dono deste registro
    int user_id {
      table = "user"
    }
  
    // Data de criação do registro
    timestamp created_at?=now
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {
      type : "btree"
      field: [{name: "user_id"}, {name: "course_id"}]
    }
  ]
}