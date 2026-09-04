import { useCallback, useEffect, useState } from "react";
import { getModels, switchModel } from "../api";

export function useModels() {
    const [models, setModels] = useState([]);
    const [currentModel, setCurrentModel] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const refreshModels = useCallback(async () => {
        try {
            const data = await getModels();

            setModels(data.models ?? []);
            setCurrentModel(data.current_model ?? null);
            setError(null);
        } catch (err) {
            console.error(err);
            setError(err.message);
        } finally {
            setLoading(false);
        }
    }, []);

    const changeModel = useCallback(async (modelName) => {
        try {
            setLoading(true);

            const data = await switchModel(modelName);

            setCurrentModel(data.model);
            setError(null);

            return data;
        } catch (err) {
            console.error(err);
            setError(err.message);
            throw err;
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        refreshModels();
    }, [refreshModels]);

    return {
        models,
        currentModel,
        loading,
        error,
        refreshModels,
        changeModel,
    };
}