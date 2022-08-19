import MaterialTable from '@material-table/core'

interface SpeciesKeyTableProps {
   data: { name: string; hasIndex: boolean }[]
   isLoading?: boolean
}

export default function SpeciesKeyTable(props: SpeciesKeyTableProps) {
   return (
      <MaterialTable
         {...props}
         columns={[
            { title: 'Name', field: 'name', sorting: true },
            {
               title: 'has Index',
               field: 'has_index',
               sorting: true,
               type: 'boolean'
            }
         ]}
         title="Species of Model"
         options={{
            pageSize: props.data.length || 5,

            paging: false,
            // @ts-expect-error
            bodyHeight: '200px',
            maxBodyHeight: '200px',

            filtering: false,
            cellStyle: {
               padding: 2,
               paddingLeft: 14,
               paddingRight: 5,
               margin: 5
            },

            headerStyle: {
               paddingLeft: 7,
               backgroundColor: '#EEE',
               padding: 2,
               margin: 2
            }
         }}
      />
   )
}
