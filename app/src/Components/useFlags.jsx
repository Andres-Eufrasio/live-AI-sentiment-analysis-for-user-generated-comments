import { useCallback, useEffect, useState } from "react";

import { getFlags } from "../api";

export function useFlags() {
    const [flags, setFlags] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [lastUpdated, setLastUpdated] = useState(null);

    const refreshFlags = useCallback(async () => {
        try {
            const data = await getFlags();

            if (Array.isArray(data)) {
                setFlags(data);
            } else if (Array.isArray(data.flags)) {
                setFlags(data.flags);
            } else if (data && typeof data === "object") {
                setFlags(Object.values(data));
            } else {
                setFlags([]);
            }

            setLastUpdated(new Date());
            setError(null);
        } catch (err) {
            console.error(err);
            setError(err.message);
            setFlags([]);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        refreshFlags();

        const interval = setInterval(refreshFlags, 2000);

        return () => clearInterval(interval);
    }, [refreshFlags]);

    return {
        flags,
        loading,
        error,
        lastUpdated,
        refreshFlags,
    };
}