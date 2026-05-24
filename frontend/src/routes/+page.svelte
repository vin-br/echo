<script lang="ts">
	import { enhance } from '$app/forms';

	let { data } = $props();

	let preview = $state<string | null>(null);
	let fileName = $state<string | null>(null);
	let analyzing = $state(false);
	let prediction = $state<{ label: string; confidence: number } | null>(null);
	let detecting = $state(false);
	let annotatedImage = $state<string | null>(null);
	let detectionMethod = $state<string | null>(null);
	let activePlot = $state(0);

	type Toast = { message: string; type: 'success' | 'error' | 'info' } | null;
	let toast = $state<Toast>(null);
	let toastTimeout: ReturnType<typeof setTimeout>;

	function handleFileChange(e: Event) {
		const input = e.target as HTMLInputElement;
		const file = input.files?.[0];
		if (file) {
			fileName = file.name;
			prediction = null;
			annotatedImage = null;
			detectionMethod = null;
			const reader = new FileReader();
			reader.onload = () => {
				preview = reader.result as string;
			};
			reader.readAsDataURL(file);
			showToast('Image added', 'success');
		} else {
			clearAll();
		}
	}

	function clearAll() {
		preview = null;
		fileName = null;
		prediction = null;
		annotatedImage = null;
		detectionMethod = null;
		const input = document.getElementById('file-input') as HTMLInputElement;
		if (input) input.value = '';
		dismissToast();
	}

	function showToast(message: string, type: 'success' | 'error' | 'info') {
		toast = { message, type };
		clearTimeout(toastTimeout);
		toastTimeout = setTimeout(dismissToast, 4000);
	}

	function dismissToast() {
		toast = null;
	}

	async function handleDetect() {
		const input = document.getElementById('file-input') as HTMLInputElement;
		const file = input.files?.[0];
		if (!file) return;

		detecting = true;
		const formData = new FormData();
		formData.append('file1', file);

		try {
			const res = await fetch('/api/detect', { method: 'POST', body: formData });
			if (res.ok) {
				const data = await res.json();
				annotatedImage = `data:image/png;base64,${data.annotated_image}`;
				detectionMethod = data.method;
				if (data.message) {
					showToast(data.message, 'info');
				} else {
					showToast(`Detection complete — ${data.detections} region(s) found`, 'success');
				}
			} else {
				showToast('Detection failed', 'error');
			}
		} catch {
			showToast('Detection failed', 'error');
		} finally {
			detecting = false;
		}
	}
</script>

<header>
	<div class="header-content">
		<h1><a href="/">ECHO</a></h1>
	</div>
</header>

<main>
	<section class="hero-shell">
		<div class="hero-content">
			<p class="eyebrow">detect, classify, annotate</p>
			<h2>Support tool. Pre-screen only.</h2>
			<p class="hero-lede">Upload a brain MRI — ECHO returns a prediction with a confidence score.</p>
			<div class="hero-highlights">
				<span class="highlight-chip">ConvNeXt Model</span>
				<span class="highlight-chip">Prediction</span>
				<span class="highlight-chip">Confidence Score</span>
				<span class="highlight-chip">YOLO Detection</span>
				<span class="highlight-chip">Models Leaderboard</span>
				<span class="highlight-chip">Training Curves</span>
			</div>
			<div class="hero-metrics">
				<article>
					<span class="metric-value"
						>{data.latency?.avg_ms != null
							? `${data.latency.avg_ms} ms`
							: '—'}</span
					>
					<span class="metric-label"
						>Avg. inference{data.latency?.count
							? ` · last ${data.latency.count}`
							: ' · no data yet'}</span
					>
				</article>
				<article>
					<span class="metric-value">4 classes</span>
					<span class="metric-label">No tumor · Glioma · Meningioma · Pituitary</span>
				</article>
			</div>
		</div>

		<div class="upload-section">
			<div class="section-header">
				<div>
					<h2>Scan Insight</h2>
					<p class="section-subtitle">Drag & drop an MRI slice or browse manually.</p>
				</div>
				<p class="card-badge">IN DEVELOPMENT</p>
			</div>
			<div class="card">
				<form
					method="POST"
					action="?/predict"
					enctype="multipart/form-data"
					use:enhance={() => {
						analyzing = true;
						return async ({ result }) => {
							analyzing = false;
							if (result.type === 'success' && result.data) {
								const d = result.data as { prediction: string; confidence: number };
								prediction = { label: d.prediction, confidence: d.confidence };
								showToast('Prediction completed', 'success');
							} else if (result.type === 'failure' && result.data) {
								showToast((result.data as { error: string }).error || 'Prediction failed', 'error');
							}
						};
					}}
				>
					<div class="card-columns">
						<div class="card-col-left">
							<div class="upload-dropzone" class:has-image={preview}>
								<input
									type="file"
									name="file"
									id="file-input"
									accept="image/*"
									onchange={handleFileChange}
								/>
								{#if !preview}
									<label for="file-input">
										<span class="drop-main">Select or drop your image</span>
										<span class="drop-sub">Max 25&nbsp;MB · PNG/JPG</span>
									</label>
								{:else if annotatedImage}
									<img src={annotatedImage} class="preview-image" alt="Annotated detection" />
								{:else}
									<img src={preview} class="preview-image" alt="Uploaded preview" />
								{/if}
							</div>
						</div>
						<div class="card-col-right">
							<div class="status-panel-vertical">
								<div class="status-header">Analysis Status</div>
								<div class="status-item">
									<span class="status-label">File</span>
									<span class="status-value" class:status-value--active={fileName}>
										{fileName || 'No file selected'}
									</span>
								</div>
								<div class="status-item">
									<span class="status-label">Prediction</span>
									<span class="status-value">
										{#if analyzing}
											Analyzing...
										{:else if prediction}
											<strong>{prediction.label}</strong>
										{:else}
											Not analyzed
										{/if}
									</span>
								</div>
								<div class="status-item">
									<span class="status-label">Confidence</span>
									<span class="status-value">
										{#if prediction}
											{prediction.confidence.toFixed(2)}%
										{:else}
											—
										{/if}
									</span>
								</div>
								<div class="status-item">
									<span class="status-label">Detection</span>
									<span class="status-value">
										{#if detecting}
											Detecting...
										{:else if detectionMethod}
											{detectionMethod === 'yolo' ? 'YOLO' : detectionMethod === 'opencv' ? 'OpenCV' : '—'}
										{:else}
											—
										{/if}
									</span>
								</div>
							</div>
						</div>
					</div>
				{#if fileName}
					<div class="button-group">
						{#if prediction}
							<button class="primary-action" type="button" onclick={handleDetect} disabled={detecting}>
								{detecting ? 'Detecting...' : 'Detect & Annotate'}
							</button>
						{:else}
							<button class="primary-action" type="submit" disabled={analyzing || detecting}>
								{analyzing ? 'Analyzing...' : 'Ask ECHO'}
							</button>
						{/if}
						<button class="secondary-action" type="button" onclick={clearAll}>Clear</button>
					</div>
				{/if}
				</form>
			</div>
		</div>
	</section>

	<section class="transparency-section">
		<div class="transparency-header">
			<h2>Transparency</h2>
			<p class="section-subtitle">
				Every model tested is shown here with its real scores. The best-performing architecture is selected for production — no cherry-picking, no hidden results.
			</p>
		</div>
		<div class="card leaderboard-card">
			<div class="card-header">
				<div>
					<h3>Models Leaderboard</h3>
					<p class="card-subtitle">Ranked by test accuracy on held-out data</p>
				</div>
			</div>
			<div class="leaderboard-container">
				{#if data.metrics.length === 0}
					<p class="empty-state">No training results available yet.</p>
				{:else}
					<table class="leaderboard-table">
						<thead>
							<tr>
								<th>Rank</th>
								<th>Model</th>
								<th>Test Accuracy</th>
								<th>Test Recall</th>
								<th>Test Macro F1</th>
								<th>Val Accuracy</th>
								<th>Batch Size</th>
								<th>Learning Rate</th>
								<th>Best Epoch</th>
							</tr>
						</thead>
						<tbody>
							{#each data.metrics as row, index}
								<tr class:rank-1={index === 0}>
									<td class="rank-cell">{index + 1}</td>
									<td class="model-cell">{row.model}</td>
									<td class="acc-cell">{(row.test_acc * 100).toFixed(2)}%</td>
									<td class="recall-cell">{row.macro_recall != null ? (row.macro_recall * 100).toFixed(2) + '%' : '—'}</td>
									<td class="f1-cell">{row.macro_f1 != null ? (row.macro_f1 * 100).toFixed(2) + '%' : '—'}</td>
									<td>{(row.val_acc * 100).toFixed(2)}%</td>
									<td>{row.batch_size}</td>
									<td>{row.lr.toExponential(1)}</td>
									<td>{row.best_epoch}</td>
								</tr>
							{/each}
						</tbody>
					</table>
				{/if}
			</div>
		</div>

		{#if data.plots && data.plots.length > 0}
			<div class="card curves-card">
				<div class="card-header">
					<div>
						<h3>Training Curves</h3>
						<p class="card-subtitle">Accuracy over epochs — how each model learned</p>
					</div>
				</div>
				<div class="carousel">
					<div class="carousel-nav">
						{#each data.plots as plotName, i}
							<button
								class="card-tab"
								class:active={activePlot === i}
								type="button"
								onclick={() => (activePlot = i)}
							>
								{plotName.replace(/-b\d+.*$/, '').replace(/-/g, ' ')}
								<span class="tab-detail">{plotName.replace(/^.*?-b/, 'b').replace(/-img.*$/, '')}</span>
							</button>
						{/each}
					</div>
					<div class="carousel-frame">
						<iframe
							src="/api/plots/{data.plots[activePlot]}"
							title="Training curves for {data.plots[activePlot]}"
							sandbox="allow-scripts"
						></iframe>
					</div>
				</div>
			</div>
		{/if}
	</section>
</main>

{#if toast}
	<div class="snackbar-container">
		<div class="snackbar snackbar--{toast.type}" role="alert" aria-live="assertive">
			<span>{toast.message}</span>
			<button type="button" class="snackbar-close" aria-label="Dismiss" onclick={dismissToast}>
				&times;
			</button>
		</div>
	</div>
{/if}

<footer>
	<div class="social-links">
		<a href="https://gitlab.com/vin-br/echo" aria-label="GitLab">
			<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="m23.6 9.593-.033-.086L20.3.98a.851.851 0 0 0-.336-.382.86.86 0 0 0-.994.056.86.86 0 0 0-.29.412l-2.204 6.748H7.528L5.324 1.066a.86.86 0 0 0-.29-.416.856.856 0 0 0-.994-.056.85.85 0 0 0-.336.384L.437 9.502l-.034.087a6.07 6.07 0 0 0 2.012 7.01l.01.008.028.02 4.97 3.722 2.458 1.86 1.496 1.13a1.01 1.01 0 0 0 1.22 0l1.496-1.13 2.458-1.86 5-3.744.012-.01a6.073 6.073 0 0 0 2.008-7.002z"/></svg>
		</a>
		<a href="https://github.com/vin-br/echo" aria-label="GitHub">
			<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M12 .297c-6.63 0-12 5.373-12 12 0 5.303 3.438 9.8 8.205 11.385.6.113.82-.258.82-.577 0-.285-.01-1.04-.015-2.04-3.338.724-4.042-1.61-4.042-1.61C4.422 18.07 3.633 17.7 3.633 17.7c-1.087-.744.084-.729.084-.729 1.205.084 1.838 1.236 1.838 1.236 1.07 1.835 2.809 1.305 3.495.998.108-.776.417-1.305.76-1.605-2.665-.3-5.466-1.332-5.466-5.93 0-1.31.465-2.38 1.235-3.22-.135-.303-.54-1.523.105-3.176 0 0 1.005-.322 3.3 1.23.96-.267 1.98-.399 3-.405 1.02.006 2.04.138 3 .405 2.28-1.552 3.285-1.23 3.285-1.23.645 1.653.24 2.873.12 3.176.765.84 1.23 1.91 1.23 3.22 0 4.61-2.805 5.625-5.475 5.92.42.36.81 1.096.81 2.22 0 1.606-.015 2.896-.015 3.286 0 .315.21.69.825.57C20.565 22.092 24 17.592 24 12.297c0-6.627-5.373-12-12-12"/></svg>
		</a>
		<a href="https://hub.docker.com/u/vinbr" aria-label="Docker Hub">
			<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M13.983 11.078h2.119a.186.186 0 0 0 .186-.185V9.006a.186.186 0 0 0-.186-.186h-2.119a.186.186 0 0 0-.185.186v1.887c0 .102.083.185.185.185m-2.954-5.43h2.118a.186.186 0 0 0 .186-.186V3.574a.186.186 0 0 0-.186-.185h-2.118a.186.186 0 0 0-.185.185v1.888c0 .102.082.185.185.186m0 2.716h2.118a.187.187 0 0 0 .186-.186V6.29a.186.186 0 0 0-.186-.185h-2.118a.186.186 0 0 0-.185.185v1.887c0 .102.082.186.185.186m-2.93 0h2.12a.186.186 0 0 0 .184-.186V6.29a.185.185 0 0 0-.185-.185H8.1a.186.186 0 0 0-.185.185v1.887c0 .102.083.186.185.186m-2.964 0h2.119a.186.186 0 0 0 .185-.186V6.29a.186.186 0 0 0-.185-.185H5.136a.186.186 0 0 0-.186.185v1.887c0 .102.084.186.186.186m5.893 2.715h2.118a.186.186 0 0 0 .186-.185V9.006a.186.186 0 0 0-.186-.186h-2.118a.186.186 0 0 0-.185.186v1.887c0 .102.082.185.185.185m-2.93 0h2.12a.185.185 0 0 0 .184-.185V9.006a.185.185 0 0 0-.184-.186h-2.12a.185.185 0 0 0-.184.186v1.887c0 .102.083.185.185.185m-2.964 0h2.119a.186.186 0 0 0 .185-.185V9.006a.186.186 0 0 0-.185-.186H5.136a.186.186 0 0 0-.186.186v1.887c0 .102.084.185.186.185m-2.92 0h2.12a.185.185 0 0 0 .184-.185V9.006a.185.185 0 0 0-.184-.186h-2.12a.186.186 0 0 0-.185.186v1.887c0 .102.083.185.185.185M23.763 9.89c-.065-.051-.672-.51-1.954-.51-.338.001-.676.03-1.01.087-.248-1.7-1.653-2.53-1.716-2.566l-.344-.199-.226.327c-.284.438-.49.922-.612 1.43-.23.97-.09 1.882.403 2.661-.595.332-1.55.413-1.744.42H.751a.751.751 0 0 0-.75.748 11.376 11.376 0 0 0 .692 4.062c.545 1.428 1.355 2.48 2.41 3.124 1.18.723 3.1 1.137 5.275 1.137.983.003 1.963-.086 2.93-.266a12.248 12.248 0 0 0 3.823-1.389c.98-.567 1.86-1.288 2.61-2.136 1.252-1.418 1.998-2.997 2.553-4.4h.221c1.372 0 2.215-.549 2.68-1.009.309-.293.55-.65.707-1.046l.098-.288Z"/></svg>
		</a>
		<a href="https://www.linkedin.com/in/vin-br/" aria-label="LinkedIn">
			<svg width="28" height="28" viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433a2.062 2.062 0 0 1-2.063-2.065 2.064 2.064 0 1 1 2.063 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
		</a>
		<a href="https://www.apache.org/licenses/LICENSE-2.0" aria-label="License"><svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/></svg></a>
	</div>
	<p>Vincent Boettcher</p>
</footer>
