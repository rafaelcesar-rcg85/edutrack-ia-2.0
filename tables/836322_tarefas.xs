table tarefas {
  auth = false

  schema {
    int id
    timestamp created_at?=now {
      visibility = "private"
    }
  
    int user_id? {
      table = "user"
    }
  
    int disc_id? {
      table = "disciplinas"
    }
  
    text nome? filters=trim
    decimal nota?
    text status? filters=trim
    date? data_entrega?
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
  ]
}