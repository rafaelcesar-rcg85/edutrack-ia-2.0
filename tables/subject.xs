table subject {
  auth = false

  schema {
    int id
    timestamp created_at?=now
    text name
    text teacher?
    int total_hours?
  
    // Foreign key to user
    int user_id {
      table = "user"
    }
  }

  index = [
    {type: "primary", field: [{name: "id"}]}
    {type: "btree", field: [{name: "created_at", op: "desc"}]}
    {type: "btree", field: [{name: "user_id"}]}
  ]
}