<template>
	<main class="app-shell">
		<Sidebar
			:active="activeItem"
			@new-recording="handleNew"
			@search="showSearch = true"
		/>

		<section class="content" :class="{ recording: isRecording }">
			<!-- Idle -->
			<div class="hero" v-show="!isRecording">
				<button
					class="mic-button"
					:class="{ live: isLive }"
					@click="onMicClick"
					aria-label="Start recording"
				>
					<FontAwesomeIcon :icon="faMicrophone" class="mic" />
				</button>
				<h2 v-if="user">
					Let’s get started, {{ user.display_name || user.email }}!
				</h2>
			</div>

			<!-- Editor -->
			<div class="rec-layout" v-show="isRecording">
				<button
					class="mic-button"
					:class="{ live: isLive }"
					@click="onMicClick"
					:aria-pressed="isLive"
				>
					<FontAwesomeIcon :icon="faMicrophone" class="mic" />
				</button>

				<aside class="transcript-pane">
					<textarea
						v-model="transcript"
						placeholder="Speak, pause to save. You can edit and it auto-saves…"
					/>
					<div class="status">
						<span v-if="isLive">Recording…</span>
						<span v-else-if="isTranscribing">Transcribing…</span>
						<span v-else-if="saveState === 'saving'">Saving…</span>
						<span v-else-if="saveState === 'saved'">Saved</span>
						<span v-else-if="saveState === 'error'" style="color: #e11d48"
							>Save failed</span
						>
					</div>
				</aside>
			</div>
		</section>

		<SearchModal
			v-model:modelValue="showSearch"
			:items="historyItems"
			@select="openTranscript"
		/>
	</main>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import Sidebar from '@/components/Sidebar.vue';
import SearchModal from '@/components/SearchModal.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faMicrophone } from '@fortawesome/free-solid-svg-icons';
import {
	me,
	listTranscripts,
	getTranscript,
	updateTranscript,
	createTranscript,
	transcribeAudio,
} from '@/client/apiClient';

const activeItem = ref('new');
const isRecording = ref(false); // editor visible
const isLive = ref(false); // mic actively recording
const isTranscribing = ref(false); // awaiting Whisper result
const showSearch = ref(false);
const saveState = ref(''); // '', 'saving', 'saved', 'error'

const user = ref(null);
const transcripts = ref([]);
const dateFilter = (iso) =>
	iso
		? new Date(iso).toLocaleDateString(undefined, {
				year: 'numeric',
				month: 'short',
				day: 'numeric',
		  })
		: '';

const historyItems = computed(() => {
	const list = transcripts.value ?? [];
	const filtered = list.filter((t) => {
		const isWebm = !!t.filename && /\.webm$/i.test(t.filename);
		const hasText = !!(t.text && t.text.trim());
		return !(isWebm && !hasText);
	});

	const source = filtered.length ? filtered : list;

	return source.map((t) => ({
		id: t.id,
		title:
			t.filename && !/\.webm$/i.test(t.filename)
				? t.filename
				: t.text?.slice(0, 80) || dateFilter(t.createdAt) || '(untitled)',
	}));
});
const currentId = ref(null);
const transcript = ref('');
const words = ref([]);

let mediaRecorder = null;
let mediaStream = null;
let chunks = [];
const recordingSupported = !!(navigator.mediaDevices && window.MediaRecorder);

onMounted(async () => {
	user.value = await me().catch(() => null);
	await refreshHistory();
});

async function refreshHistory() {
	try {
		transcripts.value = await listTranscripts();
	} catch (e) {
		console.error('Failed to list transcripts', e);
	}
}

/* New empty doc in editor (mic paused) */
async function handleNew() {
	await stopRecorderIfNeeded(false);
	isRecording.value = true;
	isLive.value = false;
	isTranscribing.value = false;
	currentId.value = null;
	transcript.value = '';
	words.value = [];
	activeItem.value = 'new';
}

/* Open existing */
async function openTranscript(item) {
	try {
		const doc = await getTranscript(item.id);
		currentId.value = doc.id;
		transcript.value = doc.text || '';
		words.value = doc.words || [];
		isRecording.value = true;
		isLive.value = false;
		isTranscribing.value = false;
		showSearch.value = false;
		activeItem.value = 'new';
	} catch (e) {
		console.error('Open transcript failed', e);
	}
}

/* ---- Mic click: start -> pause & save -> start again (append mode) ---- */
async function onMicClick() {
	if (!recordingSupported)
		return alert('Recording not supported in this browser.');
	if (!isRecording.value) return startRecording();

	if (isLive.value) {
		// PAUSE -> finalize audio, transcribe, save/append
		await pauseAndTranscribe();
	} else {
		// RESUME -> start a new take; when paused we’ll append new text
		await startRecording();
	}
}

function pickMimeType() {
	const c = [
		'audio/webm;codecs=opus',
		'audio/webm',
		'audio/ogg;codecs=opus',
		'audio/mp4', // Safari
	];
	for (const t of c) {
		if (MediaRecorder.isTypeSupported?.(t)) return t;
	}
	return '';
}

async function startRecording() {
	try {
		mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });
		chunks = [];
		const mimeType = pickMimeType();
		mediaRecorder = new MediaRecorder(
			mediaStream,
			mimeType ? { mimeType } : undefined
		);
		mediaRecorder.ondataavailable = (e) => {
			if (e.data && e.data.size) chunks.push(e.data);
		};
		mediaRecorder.start(1000); // 1s timeslice so we actually receive data while recording
		isRecording.value = true;
		isLive.value = true;
		activeItem.value = 'new';
		saveState.value = '';
	} catch (e) {
		console.error('Failed to start recording', e);
		alert('Microphone permission denied or unsupported format.');
	}
}

function stopTracks() {
	if (mediaStream) {
		mediaStream.getTracks().forEach((t) => t.stop());
		mediaStream = null;
	}
}

function stopRecorderAndGetBlob() {
	return new Promise((resolve) => {
		const parts = [...chunks];
		const onData = (e) => {
			if (e.data && e.data.size) parts.push(e.data);
		};
		const onStop = () => {
			mediaRecorder.removeEventListener('dataavailable', onData);
			mediaRecorder.removeEventListener('stop', onStop);
			const type = mediaRecorder.mimeType || parts[0]?.type || 'audio/webm';
			resolve(new Blob(parts, { type }));
		};
		mediaRecorder.addEventListener('dataavailable', onData);
		mediaRecorder.addEventListener('stop', onStop, { once: true });
		if (mediaRecorder.state !== 'inactive') mediaRecorder.stop();
		else onStop();
	});
}

async function stopRecorderIfNeeded(keepEditorOpen = true) {
	if (mediaRecorder && mediaRecorder.state !== 'inactive') {
		await new Promise((r) => {
			mediaRecorder.addEventListener('stop', r, { once: true });
			mediaRecorder.stop();
		});
	}
	mediaRecorder = null;
	stopTracks();
	isLive.value = false;
	if (!keepEditorOpen) isRecording.value = false;
}

/* Pause -> transcribe -> save/append */
async function pauseAndTranscribe() {
	try {
		isLive.value = false;
		isTranscribing.value = true;
		const blob = await stopRecorderAndGetBlob();
		await stopRecorderIfNeeded(true);
		const file = new File(
			[blob],
			`recording-${Date.now()}.${blob.type.includes('mp4') ? 'm4a' : 'webm'}`,
			{ type: blob.type }
		);

		// Send to backend (Whisper), get text
		const res = await transcribeAudio(file, { language: 'en' }); // or omit to autodetect
		const newText = (res.text || '').trim();

		// Append or create
		if (currentId.value) {
			const combined =
				(transcript.value ? transcript.value.trim() + '\n' : '') + newText;
			transcript.value = combined;
			await autoSaveNow(); // persist immediately
		} else {
			// first take -> create doc
			const doc = await createTranscript({
				text: newText,
				words: res.words || [],
			});
			currentId.value = doc.id;
			transcript.value = newText;
			words.value = res.words || [];
			saveState.value = 'saved';
		}
		await refreshHistory();
		chunks = [];
	} catch (e) {
		console.error('Transcribe failed', e);
		saveState.value = 'error';
	} finally {
		isTranscribing.value = false;
	}
}

/* ------------ Auto-save on edits (debounced) ------------ */
function debounce(fn, ms) {
	let t;
	return (...args) => {
		clearTimeout(t);
		t = setTimeout(() => fn(...args), ms);
	};
}

const debouncedSave = debounce(async () => {
	if (!currentId.value) {
		// create a doc if user starts typing before any recording
		try {
			saveState.value = 'saving';
			const doc = await createTranscript({ text: transcript.value, words: [] });
			currentId.value = doc.id;
			saveState.value = 'saved';
			await refreshHistory();
		} catch (e) {
			console.error('Create failed', e);
			saveState.value = 'error';
		}
		return;
	}
	try {
		saveState.value = 'saving';
		await updateTranscript(currentId.value, { text: transcript.value });
		saveState.value = 'saved';
	} catch (e) {
		console.error('Update failed', e);
		saveState.value = 'error';
	}
}, 600);

async function autoSaveNow() {
	// immediate save (no debounce) — used after append from a take
	if (!currentId.value) return;
	try {
		saveState.value = 'saving';
		await updateTranscript(currentId.value, { text: transcript.value });
		saveState.value = 'saved';
	} catch (e) {
		console.error('Immediate save failed', e);
		saveState.value = 'error';
	}
}

watch(transcript, (v, old) => {
	// Don’t autosave while we’re mid-transcription append
	if (isTranscribing.value) return;
	// Only autosave if editor is visible
	if (!isRecording.value) return;
	debouncedSave();
});
</script>

<style lang="scss" scoped>
.app-shell {
	height: 100vh;
}

/* keep content out from under fixed sidebar */
.content {
	margin-left: 64px;
	height: 100vh;
	box-sizing: border-box;
	display: grid;
	place-items: center;
	padding: 24px;
	--mic-size: 10rem;
	--mic-bg: #000;
	--mic-icon: #fff;
	&.recording {
		--mic-size: 8rem;
	}
}
.hero {
	text-align: center;
	h2 {
		margin-top: 16px;
	}
}

.rec-layout {
	width: 100%;
	height: 100%;
	display: grid;
	grid-template-columns: 1fr 520px;
	align-items: center;
	justify-items: center;
	padding-right: 24px;
}

/* Mic */
.mic-button {
	background: var(--mic-bg);
	color: var(--mic-icon);
	border: none;
	border-radius: 50%;
	width: var(--mic-size);
	height: var(--mic-size);
	display: inline-flex;
	align-items: center;
	justify-content: center;
	cursor: pointer;
	box-shadow: 0 10px 24px rgba(0, 0, 0, 0.1);
	transition: background 0.14s ease, transform 0.14s ease, width 0.16s ease,
		height 0.16s ease;
}
.mic-button.live {
	background: #ef4444;
}
.mic {
	font-size: calc(var(--mic-size) * 0.55);
}

/* Right pane */
.transcript-pane {
	height: 100%;
	width: 100%;
	padding: 2rem;
	background: #fff;
	border-radius: 14px;
	box-shadow: 0 8px 22px rgba(0, 0, 0, 0.1);
	display: flex;
	flex-direction: column;
	overflow: hidden;
	textarea {
		flex: 1;
		width: 95%;
		min-height: 0;
		resize: none;
		border: none;
		padding: 12px;
		line-height: 1.45;
		outline: none;
		overflow: auto;
		background: #fff;
	}
	.status {
		margin-top: 10px;
		font-size: 12px;
		color: #6b7280;
	}
}

@media (max-width: 900px) {
	.rec-layout {
		grid-template-columns: 1fr;
		align-items: start;
	}
	.transcript-pane {
		height: 70vh;
	}
}
</style>
