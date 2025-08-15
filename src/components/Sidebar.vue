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

		<div class="settings-container">
			<!-- bottom gear -->
			<button
				class="icon-btn settings"
				aria-label="Settings"
				@click="showMenu = !showMenu"
			>
				<FontAwesomeIcon :icon="faGear" />
			</button>

			<!-- popup menu -->
			<div class="settings-popup" v-show="showMenu">
				<div class="menu-item">
					<FontAwesomeIcon :icon="faUser" />
					<span>{{ username }}</span>
				</div>
				<div class="menu-item logout" @click="logoutUser">
					<FontAwesomeIcon :icon="faRightFromBracket" />
					<span>Log out</span>
				</div>
			</div>
		</div>
	</aside>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import {
	faPlus,
	faMagnifyingGlass,
	faGear,
	faRightFromBracket,
} from '@fortawesome/free-solid-svg-icons';
import { faUser } from '@fortawesome/free-regular-svg-icons';
import { ref } from 'vue';
import { logout } from '@/client/apiClient';
import { useRouter } from 'vue-router';
// Props
defineProps({
	active: { type: String, default: '' }, // 'new' | 'search' | 'history' | 'settings'
	avatar: { type: String, default: '@/assets/fantuan.png' },
});

// State
const showMenu = ref(false);
const username = ref('Zhi Kang Xie');

const router = useRouter();

// Methods
function logoutUser() {
	console.log('Logging out...');
	showMenu.value = false;
	logout();
	router.push({ name: 'landing' })
}
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

.settings-container {
	position: relative;
}

.settings-popup {
	position: absolute;
	bottom: 3rem;
	left: 1rem;
	background: white;
	border-radius: 8px;
	box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
	padding: 8px 0;
	width: 160px;
	display: flex;
	flex-direction: column;
	z-index: 50;
}

.menu-item {
	display: flex;
	align-items: center;
	gap: 8px;
	padding: 8px 12px;
	font-size: 14px;
}

.logout {
	color: red;
	cursor: pointer;
	&:hover {
		background-color: #f3f4f6;
	}
}
</style>
