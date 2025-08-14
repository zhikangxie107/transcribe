<template>
	<teleport to="body">
		<div v-show="modelValue" class="overlay" @click="onBackdrop">
			<div
				class="modal"
				ref="modal"
				role="dialog"
				aria-modal="true"
				aria-label="Search transcripts"
				@click.stop
			>
				<div class="searchbar">
					<FontAwesomeIcon :icon="faMagnifyingGlass" class="icon" />
					<input
						ref="inputEl"
						v-model="q"
						type="text"
						placeholder="Search documents..."
						@keydown.esc="close"
					/>
				</div>

				<div class="divider" />

				<ul class="results">
					<li
						v-for="item in filtered"
						:key="item.id"
						class="row"
						@click="select(item)"
						tabindex="0"
						@keydown.enter.prevent="select(item)"
					>
						<FontAwesomeIcon :icon="faFileLines" class="doc-icon" />
						<span class="title">{{ item.title }}</span>
					</li>

					<li v-if="!filtered.length" class="empty">No matches</li>
				</ul>

				<div class="footer">
					<button class="close-btn" @click="close">Close</button>
				</div>
			</div>
		</div>
	</teleport>
</template>

<script setup>
import { ref, computed, watch, onMounted, onBeforeUnmount } from 'vue';
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faMagnifyingGlass } from '@fortawesome/free-solid-svg-icons';
import { faFileLines } from '@fortawesome/free-regular-svg-icons';

const props = defineProps({
	modelValue: { type: Boolean, default: false }, 
	items: { type: Array, default: () => [] }, 
});

const emit = defineEmits(['update:modelValue', 'select']);

const q = ref('');
const inputEl = ref(null);
const modal = ref(null);

const filtered = computed(() => {
	const s = q.value.trim().toLowerCase();
	if (!s) return props.items;
	return props.items.filter((i) => i.title.toLowerCase().includes(s));
});

function close() {
	emit('update:modelValue', false);
	q.value = '';
}

function select(item) {
	emit('select', item);
	close();
}

function onBackdrop(e) {
	close();
}

// focus input when opened
watch(
	() => props.modelValue,
	(v) => {
		if (v) requestAnimationFrame(() => inputEl.value?.focus());
	}
);

// ESC at document level (extra safety)
function onKey(e) {
	if (e.key === 'Escape' && props.modelValue) close();
}
onMounted(() => document.addEventListener('keydown', onKey));
onBeforeUnmount(() => document.removeEventListener('keydown', onKey));
</script>

<style scoped>
.overlay {
	position: fixed;
	inset: 0;
	background: rgba(0, 0, 0, 0.08); /* subtle dim */
	display: grid;
	place-items: center;
	z-index: 1000;
}

.modal {
	width: clamp(520px, 50vw, 720px);
	max-width: 90vw;
	background: #fff;
	border-radius: 12px;
	box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
	overflow: hidden;
}

.searchbar {
	display: grid;
	grid-template-columns: 28px 1fr;
	align-items: center;
	padding: 10px 14px;
}
.searchbar .icon {
	opacity: 0.6;
}
.searchbar input {
	border: none;
	outline: none;
	font-size: 14px;
	padding: 8px 10px;
	background: transparent;
}

.divider {
	height: 1px;
	background: rgba(0, 0, 0, 0.1);
}

.results {
	max-height: 50vh;
	overflow: auto;
	padding: 10px 14px 6px 14px;
}
.row {
	display: grid;
	grid-template-columns: 22px 1fr;
	align-items: center;
	gap: 10px;
	padding: 10px 8px;
	border-radius: 8px;
	cursor: pointer;
}
.row:hover {
	background: #f6f7f9;
}
.row:focus {
	outline: 2px solid #e5e7eb;
}
.doc-icon {
	opacity: 0.85;
}
.title {
	font-size: 14px;
}
.empty {
	padding: 14px 8px;
	color: #888;
	font-size: 14px;
}

.footer {
	display: flex;
	justify-content: flex-end;
	padding: 10px 12px;
	background: linear-gradient(180deg, transparent, #fff 60%);
}
.close-btn {
	background: #111;
	color: #fff;
	border: none;
	padding: 8px 14px;
	border-radius: 10px;
	font-weight: 600;
	cursor: pointer;
}
</style>
