
import TextField, { StandardTextFieldProps } from '@mui/material/TextField';

import * as React from 'react';
import { useEffect } from 'react';


interface floatInputProps extends StandardTextFieldProps {
    onNumberChange?: (value: number) => void;
    numberValue?: number | null | undefined;
}




export default function IntInput(props: floatInputProps) {
    const [floatValue, setfloat] = React.useState<number>(0);
    const [stringValue, setStringValue] = React.useState<string>("0");

    const tmp_props = { ...props };

    delete tmp_props.onNumberChange;
    delete tmp_props.numberValue;

    useEffect(() => {
        setStringValue('' + props.numberValue);
    }, []);

    useEffect(() => {
        try {
            console.log(stringValue);
            setfloat(parseInt(stringValue));
            if (props.onNumberChange)
                props.onNumberChange(floatValue);
        } catch (e) {
            // Noop
        }
    }, [stringValue]);





    function handlefloatChange(event: React.ChangeEvent<HTMLInputElement>) {
        // check if target is a number
        console.log(handlefloatChange, event.target.value);
        if (event.target.value == "") {
            setStringValue("0");
        } else
            if (event.target.value.match(/^([0-9]+)$/)) {
                setStringValue(event.target.value);
            }
    }
    return (
        <TextField
            {...tmp_props}
            value={stringValue}
            onChange={handlefloatChange}
            type="number"
            inputProps={{
                inputMode: 'numeric',
                pattern: '/^-?\d+(?:\.\d+)?$/g'
            }}
        />


    );
}

