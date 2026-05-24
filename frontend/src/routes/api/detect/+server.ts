import { env } from '$env/dynamic/private';
import { json } from '@sveltejs/kit';
import type { RequestHandler } from './$types';

const getBackendUrl = () => env.BACKEND_URL || 'http://localhost:8000';

export const POST: RequestHandler = async ({ request }) => {
	const formData = await request.formData();
	const file = formData.get('file1') as File;

	if (!file || !file.name || file.size === 0) {
		return json({ error: 'Please select an image.' }, { status: 400 });
	}

	const backendForm = new FormData();
	backendForm.append('file1', file);

	try {
		const res = await fetch(`${getBackendUrl()}/api/detect`, {
			method: 'POST',
			body: backendForm
		});

		if (!res.ok) {
			const err = await res.json().catch(() => ({ detail: 'Detection failed' }));
			return json({ error: err.detail || 'Detection failed' }, { status: res.status });
		}

		return json(await res.json());
	} catch {
		return json({ error: 'Backend service unavailable.' }, { status: 503 });
	}
};
