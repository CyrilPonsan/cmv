/**
 * @file patients-list.ts
 * @description Columns for the patients list
 * @author [@CyrilPonsan](https://github.com/CyrilPonsan)
 */

export const patientsListColumns = [
  {
    field: 'civilite',
    header: 'civilite',
    sortable: false
  },
  {
    field: 'nom',
    header: 'lastname',
    sortable: true
  },
  {
    field: 'prenom',
    header: 'firstname',
    sortable: true
  },
  {
    field: 'date_de_naissance',
    header: 'birth_date',
    sortable: true
  },
  {
    field: 'telephone',
    header: 'phone_number',
    sortable: false
  },
  {
    field: 'email',
    header: 'email',
    sortable: true
  }
]
