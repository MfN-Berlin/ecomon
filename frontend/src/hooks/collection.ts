import { useEffect, useState } from "react";


interface CollectionInfo {
    name: string;
    species_list: string[];
    records_count: number;
    predictions_count: number;
    indicated_species_columns: string[];
}

interface Species {
    name: string;
    has_index: boolean;
}

export function useCollectionList() {

    const [collectionList, setCollectionsList] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);
    function fetchCollections() {
        fetch('http://127.0.0.1:8000/prefix/list')
            .then(res => res.json())
            .then(data => {
                setCollectionsList(data);
                setLoading(false)
            });

    }
    useEffect(() => {
        setLoading(true)
        fetchCollections()

    }, []);


    return { collectionList, loading };
}

export function useCollectionInfo(collectionName: string | undefined) {
    const [collectionInfo, setCollectionInfo] = useState<CollectionInfo>();
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchCollectionInfo() {
            fetch('http://127.0.0.1:8000/prefix/' + collectionName)
                .then(res => res.json())
                .then(data => {
                    setCollectionInfo(data)
                    setLoading(false)
                });
        }
        setLoading(true);
        fetchCollectionInfo()
    }, [collectionName]);

    return { collectionInfo, loading };
}

export function useCollectionSpeciesList(collectionName: string | undefined) {
    const [collectionSpeciesList, setCollectionSpeciesList] = useState<Species[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function fetchCollectionSpeciesList() {
            fetch('http://127.0.0.1:8000/prefix/' + collectionName + '/species')
                .then(res => res.json())
                .then(data => {
                    // sort Array of Species by name
                    data.sort((a: Species, b: Species) => {


                        if (a.name < b.name) {
                            return -1;
                        }
                        if (a.name > b.name) {
                            return 1;
                        }
                        return 0;
                    });
                    setCollectionSpeciesList(data);
                    setLoading(false)
                });
        }
        setLoading(true);
        fetchCollectionSpeciesList()
    }, [collectionName]);

    return { collectionSpeciesList, loading };
}






interface QueryParameters {
    start_datetime?: Date | null;
    end_datetime?: Date | null;
    species: string;
    threshold: number;
}
interface QueryResponse {
    predictions_count: number
    species_count: number
}

export function useCollectionPredictionQuery(collectionName: string | undefined) {
    const [predictionQueryResponse, setCollectionPredictionQuery] = useState<QueryResponse>();
    const [loading, setLoading] = useState(false);

    const abortController = new AbortController();

    function updateQuery(queryParameters: QueryParameters) {
        if (loading) {
            abortController.abort()
            setLoading(false);

        }

        setLoading(true);

        fetch('http://127.0.0.1:8000/prefix/' + collectionName + '/predictions/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            signal: abortController.signal,
            body: JSON.stringify(queryParameters)
        }).then(res => res.json())
            .then(data => {
                setCollectionPredictionQuery(data)
                setLoading(false)
            });
    }
    function abortQuery() {
        if (loading) {
            abortController.abort()
            setLoading(false);
        }
    }
    function clearResonse() {
        setCollectionPredictionQuery(undefined)

    }


    return { predictionQueryResponse, loading, updateQuery, abortQuery, clearResonse };

}