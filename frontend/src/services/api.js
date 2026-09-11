const BASE_URL = '';

export async function createProject(payload) {
  const res = await fetch(`${BASE_URL}/api/projects`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to create project' }));
    throw new Error(err.detail || 'Failed to create project');
  }
  return res.json();
}

export async function listProjects() {
  const res = await fetch(`${BASE_URL}/api/projects`);
  if (!res.ok) throw new Error('Failed to fetch projects');
  return res.json();
}

export async function getProject(projectId) {
  const res = await fetch(`${BASE_URL}/api/projects/${projectId}`);
  if (!res.ok) throw new Error('Failed to load project details');
  return res.json();
}

export async function approveAndGenerate(payload) {
  const res = await fetch(`${BASE_URL}/api/generation/approve`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to start generation' }));
    throw new Error(err.detail || 'Failed to start generation');
  }
  return res.json();
}

export async function getGenerationStatus(jobId) {
  const res = await fetch(`${BASE_URL}/api/generation/status/${jobId}`);
  if (!res.ok) throw new Error('Failed to fetch job status');
  return res.json();
}

export async function regenerateSegment(payload) {
  const res = await fetch(`${BASE_URL}/api/generation/regenerate-segment`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to trigger partial regeneration');
  return res.json();
}

export async function uploadAsset(formData) {
  const res = await fetch(`${BASE_URL}/api/assets/upload`, {
    method: 'POST',
    body: formData
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Failed to upload asset' }));
    throw new Error(err.detail || 'Failed to upload asset');
  }
  return res.json();
}

export async function getAdminMetrics() {
  const res = await fetch(`${BASE_URL}/api/admin/metrics`);
  if (!res.ok) throw new Error('Failed to fetch admin metrics');
  return res.json();
}

export async function publishVideo(payload) {
  const res = await fetch(`${BASE_URL}/api/publish`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to publish video');
  return res.json();
}
