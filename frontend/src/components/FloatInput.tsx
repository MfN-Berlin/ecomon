
import TextField, { StandardTextFieldProps } from '@mui/material/TextField';

import * as React from 'react';
import { useEffect } from 'react';


interface FloatInputProps extends StandardTextFieldProps {
    onNumberChange?: (value: number) => void;
    numberValue?: number | null | undefined;
}




export default function FloatInput(props: FloatInputProps) {
    const [floatValue, setFloat] = React.useState<number>(0);
    const [stringValue, setStringValue] = React.useState<string>("0");

    const tmp_props = { ...props };

    delete tmp_props.onNumberChange;
    delete tmp_props.numberValue;

    useEffect(() => {
        setStringValue('' + props.numberValue);
    }, []);

    useEffect(() => {
        try {
            setFloat(parseFloat(stringValue));
            if (props.onNumberChange)
                props.onNumberChange(floatValue);
        } catch (e) {
            // Noop
        }
    }, [stringValue]);





    function handleFloatChange(event: React.ChangeEvent<HTMLInputElement>) {
        // check if target is a number
        if (event.target.value == "") {
            setStringValue("0");
        } else
            if (event.target.value.match(/^([0-9]+([.]?[0-9]*)?|[.][0-9]+)$/)) {
                setStringValue(event.target.value);
            }
    }
    return (
        <TextField
            {...tmp_props}
            value={stringValue}
            onChange={handleFloatChange}
        />

    );
}
