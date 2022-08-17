
import TextField, { StandardTextFieldProps } from '@mui/material/TextField';

import * as React from 'react';
import { useEffect } from 'react';


interface NumberInputProps extends StandardTextFieldProps {
    onNumberChange?: (value: number) => void;
    numberValue?: number | null | undefined;
    numberType?: "int" | "float";
}




export default function NumberInput(props: NumberInputProps) {
    const [numberValue, setNumberValue] = React.useState<number>(0);
    const [stringValue, setStringValue] = React.useState<string>("0");

    const tmp_props = { ...props };

    delete tmp_props.onNumberChange;
    delete tmp_props.numberValue;
    delete tmp_props.numberType;

    const regexp = props.numberType == "int" ? /^([0-9]+)$/ : /^([0-9]+([.]?[0-9]*)?|[.][0-9]+)$/;
    const parseFunction = props.numberType == "int" ? parseInt : parseFloat;

    useEffect(() => {
        setStringValue('' + props.numberValue);
    }, []);

    useEffect(() => {
        const tmp = parseFunction(stringValue);
        if (!isNaN(tmp)) {
            setNumberValue(tmp);

        } else {
            setNumberValue(0);

        }
    }, [stringValue]);
    useEffect(() => {
        if (props.onNumberChange) {
            console.log("NumberInput: onNumberChange: " + numberValue);
            props.onNumberChange(numberValue);
        }

    }, [numberValue]);






    function handleNumberChange(event: React.ChangeEvent<HTMLInputElement>) {
        // check if target is a number
        if (event.target.value == "") {
            setStringValue("");
            setNumberValue(0);
        } else
            ///^([0-9]+([.]?[0-9]*)?|[.][0-9]+)$/
            if (event.target.value.match(regexp)) {
                setStringValue(event.target.value);
            }
    }
    return (
        <TextField
            {...tmp_props}
            value={stringValue}
            onChange={handleNumberChange}
        />

    );
}
