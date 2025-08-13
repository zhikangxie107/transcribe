<template>
	<aside class="sidebar">
		<!-- top actions -->
		<nav class="stack">
			<button
				class="icon-btn"
				:class="{ active: active === 'new' }"
				@click="$emit('new-recording')"
				aria-label="New recording"
			>
				<FontAwesomeIcon :icon="faPlus" />
			</button>

			<button
				class="icon-btn"
				:class="{ active: active === 'search' }"
				@click="$emit('search')"
				aria-label="Search transcripts"
			>
				<FontAwesomeIcon :icon="faMagnifyingGlass" />
			</button>
		</nav>

		<!-- bottom gear -->
		<button
			class="icon-btn settings"
			aria-label="Settings"
		>
			<FontAwesomeIcon :icon="faGear" />
		</button>
	</aside>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faPlus, faMagnifyingGlass, faGear } from '@fortawesome/free-solid-svg-icons';

// Props
defineProps({
	active: { type: String, default: '' }, // 'new' | 'search' | 'history' | 'settings'
	avatar: { type: String, default: '@/assets/fantuan.png' },
});

// Emits: 'new-recording', 'search', 'open-history', 'open-settings', 'open-profile'
</script>

<style lang="scss" scoped>
.sidebar {
	position: fixed;
	inset: 0 auto 0 0;
	width: 55px;
	display: flex;
	flex-direction: column;
	justify-content: space-between;
	padding: 12px 8px;
	border-right: 1px solid rgba(0, 0, 0, 0.08);
	backdrop-filter: blur(10px);
	z-index: 20;
}

.stack {
	display: grid;
	gap: 8px;
	padding-left: 0.25rem;
}

/* icon button */
.icon-btn {
	height: 44px;
	width: 44px;
	background: transparent;
	display: grid;
	place-items: center;
	font-size: 18px;
	transition: transform 0.06s ease, background 0.15s ease, box-shadow 0.15s ease;
	border: none;
	border-radius: 10%;

	&:hover {
		background: rgba(0, 0, 0, 0.04); // subtle gray
		box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1); // light depth
		transform: scale(1.05); // slight pop effect
	}
}
</style>
