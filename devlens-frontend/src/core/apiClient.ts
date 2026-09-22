const BASE_URL = import.meta.env.VITE_API_URL || '/api/v1';
const TIMEOUT_MS = 30_000; // 30 seconds for AI calls
const INGEST_TIMEOUT_MS = 180_000;
const AI_TIMEOUT_MS = 300_000;

async function throwApiError(res: Response, endpoint: string): Promise<never> {
    let detail = '';
    try {
        const payload = await res.json();
        detail = typeof payload.detail === 'string' ? payload.detail : '';
    } catch {
        // The server may return a non-JSON error page.
    }
    throw new Error(`API error ${res.status}: ${detail || endpoint}`);
}

function fetchWithTimeout(
    url: string,
    options: RequestInit = {},
    timeoutMs = TIMEOUT_MS,
): Promise<Response> {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    return fetch(url, { ...options, signal: controller.signal }).finally(() => clearTimeout(timer));
}

export const apiClient = {
    get: async (endpoint: string) => {
        let res: Response;
        try {
            res = await fetchWithTimeout(`${BASE_URL}${endpoint}`);
        } catch (err: any) {
            if (err.name === 'AbortError') throw new Error(`Request timed out: ${endpoint}`);
            throw new Error(`Network error: ${err.message}`);
        }
        if (!res.ok) await throwApiError(res, endpoint);
        return res.json();
    },
    post: async (endpoint: string, body?: any) => {
        let res: Response;
        try {
            res = await fetchWithTimeout(`${BASE_URL}${endpoint}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: body ? JSON.stringify(body) : undefined,
            }, endpoint === '/repository/ingest'
                ? INGEST_TIMEOUT_MS
                : endpoint === '/explain' || endpoint === '/intent' || endpoint === '/chatbot'
                    ? AI_TIMEOUT_MS
                    : TIMEOUT_MS);
        } catch (err: any) {
            if (err.name === 'AbortError') throw new Error(`Request timed out: ${endpoint}`);
            throw new Error(`Network error: ${err.message}`);
        }
        if (!res.ok) await throwApiError(res, endpoint);
        const contentType = res.headers.get('content-type');
        if (contentType && contentType.includes('application/json')) {
            return res.json();
        }
        return res.text();
    },

    // --- Phase 6: Good First Issues & PR History ---
    getRecommendedIssues: async (owner: string, repo: string) => {
        return apiClient.get(`/issues/recommend/${owner}/${repo}`);
    },

    getPRHistory: async (owner: string, repo: string) => {
        return apiClient.get(`/history/${owner}/${repo}`);
    },

    // --- Phase 7: Gatekeeper ---
    getGatekeeperStatus: async (owner: string, repo: string) => {
        return apiClient.get(`/gatekeeper/${owner}/${repo}`);
    },

    // --- Phase 7/8: Architect Chatbot ---
    startMission: async (owner: string, repo: string, issueNumber: number, message: string, userProfile: any) => {
        return apiClient.post('/chatbot', {
            owner,
            repo,
            issue_number: issueNumber,
            message,
            user_profile: userProfile
        });
    },

    sendMissionUpdate: async (
        owner: string,
        repo: string,
        message: string,
        missionId: string,
        currentStep: number | null,
        type: 'user_chat' | 'terminal_output',
        userProfile: any
    ) => {
        return apiClient.post('/chatbot', {
            owner,
            repo,
            message,
            mission_id: missionId,
            current_step: currentStep,
            type,
            user_profile: userProfile
        });
    }
};
