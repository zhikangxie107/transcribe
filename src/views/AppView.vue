<template>
	<main class="app-shell">
		<Sidebar
			:active="activeItem"
			:avatar="avatarUrl"
			@new-recording="handleNew"
			@search="showSearch = true"
		/>

		<section class="content" :class="{ recording: isRecording }">
			<!-- Initial (idle) state -->
			<div class="hero" v-show="!isRecording">
				<button
					class="mic-button"
					@click="toggleRecording"
					aria-label="Start recording"
				>
					<FontAwesomeIcon :icon="faMicrophone" class="mic" />
				</button>
				<h2>Let’s get started, Zhi!</h2>
			</div>

			<!-- Recording state -->
			<div class="rec-layout" v-show="isRecording">
				<button
					class="mic-button"
					@click="toggleRecording"
					aria-label="Stop recording"
					:aria-pressed="isRecording"
				>
					<FontAwesomeIcon :icon="faMicrophone" class="mic" />
				</button>

				<aside class="transcript-pane">
					<textarea
						v-model="transcript"
						placeholder="Your transcript will appear here. You can edit it before saving…"
					/>
					<div class="actions">
						<button class="save" @click="saveTranscript">Save</button>
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
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import Sidebar from '@/components/Sidebar.vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faMicrophone } from '@fortawesome/free-solid-svg-icons';
import SearchModal from '@/components/SearchModal.vue';

const router = useRouter();
const activeItem = ref('new');
const isRecording = ref(false);
const transcript = ref(''); // put live transcript here as you capture audio
const showSearch = ref(false);

function handleNew() {
	activeItem.value = 'new';
}

const historyItems = ref([
	{ id: 't1', title: 'How my summer went…' },
	{ id: 't2', title: 'Apple vs Samsung' },
]);

function openTranscript(item) {
	// route or load the transcript
	// e.g., router.push({ name: 'transcript', params: { id: item.id } })
	console.log('Open:', item);
}
function toggleRecording() {
	isRecording.value = !isRecording.value;
	// TODO: start/stop your recorder here
}

function saveTranscript() {
	// persist transcript.value somewhere (emit, API call, etc.)
	console.log('Saved transcript:', transcript.value);
}
</script>

<style lang="scss" scoped>
.app-shell {
	height: 100vh; /* exact viewport height */
}

/* keep content out from under fixed sidebar */
.content {
	margin-left: 64px;
	height: 100vh; /* exact, not min-height */
	box-sizing: border-box; /* include padding in the height */
	display: grid;
	place-items: center;
	padding: 24px;

	/* mic defaults (idle) */
	--mic-size: 10rem;
	--mic-bg: #000;
	--mic-icon: #fff;

	&.recording {
		--mic-size: 8rem;
		--mic-bg: #ef4444;
		--mic-icon: #fff;
		place-items: stretch; /* let rec-layout control placement */
	}
}

/* Initial center */
.hero {
	text-align: center;
	h2 {
		margin-top: 16px;
	}
}

/* Recording layout fills the viewport area (minus padding already handled) */
.rec-layout {
	width: 100%;
	height: 100%; /* consume the full .content area */
	display: grid;
	grid-template-columns: 1fr 520px;
	align-items: center; /* center the mic vertically */
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
	transition: background 140ms ease, transform 140ms ease, width 160ms ease,
		height 160ms ease;
	&:hover {
		transform: scale(1.03);
	}
	&:active {
		transform: scale(0.98);
	}
}
.mic {
	font-size: calc(var(--mic-size) * 0.55);
}

/* Right pane fits without forcing page scroll */
.transcript-pane {
	height: 100%;
	width: 100%;
	padding: 1.5rem;
	background: #fff;
	border-radius: 14px;
	box-shadow: 0 8px 22px rgba(0, 0, 0, 0.1);
	display: flex;
	flex-direction: column;
	overflow: hidden; /* keep rounded corners clean */

	textarea {
		flex: 1; /* fills available space */
		width: 95%;
		min-height: 0; /* allow flex child to shrink */
		resize: none;
		border: none;
		padding: 12px;
		line-height: 1.45;
		outline: none;
		overflow: auto; /* only the text scrolls */
		background: #fff;
	}

	.actions {
		display: flex;
		justify-content: flex-end;
		gap: 8px;
		margin-top: 12px;
		margin-right: 1rem;
	}

	.save {
		background: #111;
		color: #fff;
		border: none;
		padding: 10px 20px;
		border-radius: 12px;
		font-weight: 600;
		cursor: pointer;
	}
}

/* Responsive */
@media (max-width: 900px) {
	.rec-layout {
		grid-template-columns: 1fr;
		align-items: start;
	}
	.transcript-pane {
		height: 70vh;
	} /* still no page scroll */
}
</style>
