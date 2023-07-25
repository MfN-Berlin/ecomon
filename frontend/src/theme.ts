import { createTheme } from '@mui/material/styles';

const theme = createTheme({
   spacing: 2, // Adjust spacing between components
   typography: {
      fontSize: 12, // Adjust font size
   },
   components: {
      MuiButton: {
         defaultProps: {
            size: 'small',
         },
      },
      MuiFilledInput: {
         defaultProps: {
            margin: 'dense',
         },
      },
      MuiFormControl: {
         defaultProps: {
            margin: 'dense',
         },
      },
      MuiFormHelperText: {
         defaultProps: {
            margin: 'dense',
         },
      },
      MuiIconButton: {
         defaultProps: {
            size: 'small',
         },
      },
      MuiInputBase: {
         defaultProps: {
            margin: 'dense',
         },
      },
      MuiInputLabel: {
         defaultProps: {
            margin: 'dense',
         },
      },
      MuiListItem: {
         defaultProps: {
            dense: true,
         },
      },
      MuiOutlinedInput: {
         defaultProps: {
            margin: 'dense',
         },
      },
      MuiFab: {
         defaultProps: {
            size: 'small',
         },
      },
      MuiTable: {
         defaultProps: {
            size: 'small',
         },
      },
      MuiTextField: {
         defaultProps: {
            margin: 'dense',
         },
      },
      MuiToolbar: {
         defaultProps: {
            variant: 'dense',
         },
      },
   },
});

export default theme;
