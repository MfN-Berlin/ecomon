import * as React from 'react';
import { useEffect, useState } from "react";
import Typography from '@mui/material/Typography';
import { useParams } from 'react-router-dom';
import {
    useCollectionSpeciesList,
    useCollectionPredictionQuery

} from '../hooks/collection';

import { usePredictionCount } from '../hooks/predictions';

import {

    useRecordCount,
    useRecordDuration,
    useFirstRecord,
    useLastRecord,
} from '../hooks/records';

import Paper from '@mui/material/Paper';
import Box from '@mui/material/Box';
import Grid from '@mui/material/Unstable_Grid2';
import TextField from '@mui/material/TextField';
import Stack from "@mui/material/Stack";
import { AdapterDateFns } from '@mui/x-date-pickers/AdapterDateFns';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DateTimePicker } from '@mui/x-date-pickers/DateTimePicker';
import DownloadIcon from '@mui/icons-material/Download';
import Select from 'react-select'
import { duration } from 'moment';

import SendIcon from '@mui/icons-material/Send';
import Button from '@mui/material/Button';

import CircularProgress from '@mui/material/CircularProgress';
import Divider from '@mui/material/Divider';
import NumberInput from '../components/NumberInput';

interface CollectionProps {
    children?: React.ReactNode;
}



function firstLetterUpperAndReplaceSpace(str: string) {
    return (str.charAt(0).toUpperCase() + str.substr(1).toLowerCase()).replace(/_/g, ' ');
}


export default function Collection(props: CollectionProps) {
    const { id } = useParams();
    const { collectionSpeciesList, loading: speciesLoading } = useCollectionSpeciesList(id);
    const { predictionCount, loading: predictionLoading } = usePredictionCount(id);
    const { recordCount, loading: recordLoading } = useRecordCount(id);
    const { recordDuration, loading: durationLoading } = useRecordDuration(id);
    const { firstRecord, loading: firstRecordLoading } = useFirstRecord(id);
    const { lastRecord, loading: lastRecordLoading } = useLastRecord(id);
    const { predictionQueryResponse, loading: queryLoading, updateQuery, abortQuery, clearResonse } = useCollectionPredictionQuery(id);


    const [selectedSpecies, setSelectedSpecies] = useState<string>();
    const [from, setFrom] = useState<Date | null>();
    const [until, setUntil] = useState<Date | null>();
    const [threshold, setThreshold] = useState<number>(0);
    const [sampleSize, setSampleSize] = useState<number>(100);
    // effects
    useEffect(() => {
        setFrom(firstRecord ? firstRecord.record_datetime : null);
    }, [firstRecord]);
    useEffect(() => {
        setUntil(lastRecord ? lastRecord.record_datetime : null);
    }, [lastRecord]);

    // effect clear prediction query response on change
    useEffect(() => {
        abortQuery();
        clearResonse();
    }, [selectedSpecies, from, until, threshold]);



    // Event handlers
    function handleQueryButtonClick() {
        if (selectedSpecies)
            updateQuery({
                species: selectedSpecies,
                start_datetime: from,
                end_datetime: until,
                threshold: threshold
            });
    }
    // download file from url
    function handleDownloadButtonClick() {
        const link = document.createElement('a');
        link.href = `http://localhost:8000/random_sample?prefix=${id}&species=${selectedSpecies}&sample_size=${sampleSize}&start_datetime=${from?.toISOString()}&end_datetime=${until?.toISOString()}&threshold=${threshold}`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }


    return (<Box sx={{ flexGrow: 1, padding: 2 }}>
        <LocalizationProvider dateAdapter={AdapterDateFns}>
            <Grid container spacing={1}>
                <Grid xs={12} md={4} xl={2}>


                    <Paper sx={{
                        padding: 1,

                    }} >
                        <Stack direction="column" spacing={2}>

                            <Typography variant="h6" component="h6" align='left' sx={{
                                marginTop: 1,
                                marginLeft: 2,
                                paddingBottom: 2
                            }}>
                                Stats
                            </Typography>


                            <TextField id="recordCount" label="Recording Count" variant="standard"

                                value={recordLoading ? "Loading..." : recordCount}
                                InputProps={{
                                    readOnly: true,

                                }}
                            />
                            <TextField id="recordDuration" label="Duration" variant="standard"

                                value={durationLoading ? "loading..." : duration(recordDuration, 'seconds').humanize()}
                                InputProps={{
                                    readOnly: true,

                                }}
                            />
                            <TextField id="predictionCount" label="Prediction Count" variant="standard"

                                value={predictionLoading ? "loading..." : predictionCount}
                                InputProps={{
                                    readOnly: true,

                                }} />
                            <DateTimePicker
                                renderInput={(props) => <TextField {...props} />}
                                label="First Recording"
                                value={firstRecord?.record_datetime}
                                readOnly={true}
                                ampm={false}
                                loading={firstRecordLoading}
                                onChange={(date) => { }}

                            />
                            <DateTimePicker
                                renderInput={(props) => <TextField {...props} />}
                                label="Last Recording"
                                value={lastRecord?.record_datetime}
                                readOnly={true}
                                ampm={false}
                                loading={lastRecordLoading}
                                onChange={(date) => { }}
                            />






                        </Stack>
                    </Paper>

                </Grid>
                {/* <Grid xs={12} md={7} xl={4} margin="4px">
                    <SpeciesKeyTable isLoading={speciesLoading} data={
                        collectionSpeciesList.sort().map(item => ({
                            name: firstLetterUpperAndReplaceSpace(item.name), hasIndex: item.has_index
                        })) || []} />

                </Grid> */}

                <Grid xs={12} md={4} >
                    <Paper sx={{


                        padding: 1,

                    }} >
                        <Stack direction="column" spacing={2}>

                            <Typography variant="h6" component="h6" align='left' sx={{
                                marginTop: 1,
                                marginLeft: 2,
                                paddingBottom: 2
                            }}>
                                Query Parameters
                            </Typography>
                            <DateTimePicker
                                renderInput={(props) => <TextField {...props} />}
                                label="from"
                                value={firstRecord?.record_datetime}
                                minDateTime={firstRecord?.record_datetime}
                                maxDateTime={lastRecord?.record_datetime}
                                ampm={false}
                                loading={firstRecordLoading || lastRecordLoading}
                                onChange={(newValue) => {
                                    setFrom(newValue);
                                }}
                            />
                            <DateTimePicker
                                renderInput={(props) => <TextField {...props} />}
                                label="until"
                                value={lastRecord?.record_datetime}
                                minDateTime={firstRecord?.record_datetime}
                                maxDateTime={lastRecord?.record_datetime}
                                ampm={false}
                                loading={firstRecordLoading || lastRecordLoading}
                                onChange={(newValue) => {
                                    console.log("changed", newValue);
                                    setUntil(newValue);
                                }}
                            />

                            <Select
                                isClearable
                                isLoading={speciesLoading}
                                onChange={(newValue) => {

                                    if (newValue)
                                        setSelectedSpecies(newValue.value);
                                    else
                                        setSelectedSpecies(undefined);
                                }}
                                options={
                                    collectionSpeciesList.filter(x => x.has_index).map(x => ({ value: x.name, label: firstLetterUpperAndReplaceSpace(x.name) }))} />
                            <NumberInput
                                numberValue={threshold}
                                numberType="float"
                                onNumberChange={setThreshold}
                                label=" >= threshold" />

                            <Button variant="contained" disabled={!selectedSpecies} endIcon={<SendIcon />} sx={{
                                padding: 1.5,
                            }} onClick={handleQueryButtonClick}> Query</Button>


                        </Stack>
                    </Paper>
                </Grid>

                <Grid xs={12} md={4} >
                    <Paper sx={{


                        padding: 1,

                    }} >
                        <Stack direction="column" spacing={2}>

                            <Typography variant="h6" component="h6" align='left' sx={{
                                marginTop: 1,
                                marginLeft: 2,
                                paddingBottom: 2
                            }}>
                                Query Results
                            </Typography>
                            {predictionQueryResponse && !queryLoading ? (
                                <React.Fragment>
                                    <TextField id="predictionsCount" label="Predictions count" variant="standard"

                                        value={queryLoading ? "Loading..." : predictionQueryResponse?.predictions_count}
                                        InputProps={{
                                            readOnly: true,

                                        }}
                                    />
                                    <TextField id="speciesCount" label="Predictions over Threshold" variant="standard"

                                        value={durationLoading ? "loading..." : predictionQueryResponse?.species_count}
                                        InputProps={{
                                            readOnly: true,

                                        }}

                                    />
                                    <Divider light />
                                    <Typography variant="h6" component="h6" align='left' sx={{
                                        marginTop: 1,
                                        marginLeft: 2,
                                        paddingBottom: 0.5
                                    }}>
                                        Create Random Sample
                                    </Typography>
                                    <NumberInput label="Sample Size"
                                        numberType='int'
                                        numberValue={sampleSize}
                                        onNumberChange={setSampleSize}></NumberInput>
                                    <Button color="secondary" variant="contained" disabled={!selectedSpecies} endIcon={<DownloadIcon />} sx={{

                                        padding: 1.5,
                                    }} onClick={handleDownloadButtonClick}> Download Random Sample</Button>



                                </React.Fragment>
                            ) : (queryLoading ?
                                <Grid ><CircularProgress /></Grid> : "")}


                        </Stack>
                    </Paper>
                </Grid>

            </Grid>
        </LocalizationProvider>
    </Box >



    )

}


