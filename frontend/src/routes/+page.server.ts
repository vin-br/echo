import { env } from '$env/dynamic/private';
import { fail } from '@sveltejs/kit';
import type { Actions, PageServerLoad } from './$types';

const getBackendUrl = () => env.BACKEND_URL || 'http://localhost:8000';

export const load: PageServerLoad = async () => {
	try {
		const [metricsRes, latencyRes, plotsRes] = await Promise.all([
			fetch(`${getBackendUrl()}/api/metrics`),
			fetch(`${getBackendUrl()}/api/latency`),
			fetch(`${getBackendUrl()}/api/plots`)
		]);
		const metrics = metricsRes.ok ? await metricsRes.json() : [];
		const latency = latencyRes.ok
			? await latencyRes.json()
			: { avg_ms: null, count: 0 };
		const plots: string[] = plotsRes.ok ? await plotsRes.json() : [];
		return { metrics, latency, plots };
	} catch {
		return { metrics: [], latency: { avg_ms: null, count: 0 }, plots: [] };
	}
};

export const actions = {
	predict: async ({ request }) => {
		const data = await request.formData();
		const file = data.get('file') as File;

		if (!file || !file.name || file.size === 0) {
			return fail(400, { error: 'Please select an image before submitting.' });
		}

		if (file.size > 25 * 1024 * 1024) {
			return fail(400, { error: 'Image exceeds the 25 MB limit.' });
		}

		const backendForm = new FormData();
		backendForm.append('file1', file);

		try {
			const res = await fetch(`${getBackendUrl()}/api/predict`, {
				method: 'POST',
				body: backendForm
			});

			if (!res.ok) {
				const err = await res.json().catch(() => ({ detail: 'Prediction failed' }));
				return fail(res.status, { error: err.detail || 'Prediction failed' });
			}

			const result = await res.json();
			return { success: true, prediction: result.prediction, confidence: result.confidence };
		} catch {
			return fail(503, { error: 'Backend service unavailable. Please try again later.' });
		}
	}
} satisfies Actions;
