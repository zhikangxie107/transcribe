<template>
	<section class="landing">
		<!-- Background -->
		<div class="blob tl"></div>
		<div class="blob tr"></div>
		<div class="blob bl"></div>
		<div class="blob br"></div>

		<div class="content">
			<FontAwesomeIcon class="icon" :icon="faMicrophoneLines" />
			<div class="title">
				<p>Welcome to</p>
				<p class="name">Transcribe</p>
			</div>
			<div class="action">
				<button class="primary" @click="goToLogin">Log in</button>
				<button class="outline" @click="goToSignup">Sign up</button>
			</div>
		</div>
	</section>
</template>

<script setup>
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome';
import { faMicrophoneLines } from '@fortawesome/free-solid-svg-icons';

import { useRouter } from 'vue-router';

const router = useRouter();

const goToLogin = () => {
	router.push('/login');
};

const goToSignup = () => {
	router.push('/signup');
};
</script>

<style lang="scss" scoped>
@use '@/assets/styles.scss' as *;

.landing {
	position: relative;
	min-height: 100vh;
	display: grid;
	place-items: center;
	overflow: hidden;
}

.content {
	.icon {
		height: 20rem;
		width: 20rem;
	}

	.title {
		display: flex;
		gap: 0.5rem;

		p {
			font-weight: bold;
			font-size: 3rem;
		}

		.name {
			color: $magenta;
		}
	}

	.action {
		display: flex;
		gap: 10rem;
		padding-left: 0.5rem;

		button {
			font-size: 2rem;
			font-weight: 600;
			padding: 0.5rem 1.25rem;
			border-radius: 20px;
			cursor: pointer;
			border: 1px solid transparent;
			transition: all 0.2s ease-in-out;

			&.primary {
				background-color: $black; /* black background */
				color: #fff; /* white text */
				&:hover {
					background-color: #222; /* slightly lighter black */
				}
			}

			&.outline {
				background-color: $white;
				border-color: #000; /* black border */
				color: #000;
				&:hover {
					background-color: $grey;
					color: #fff;
				}
			}
		}
	}
}

/* Corner positions */
.tl {
	top: -200px;
	left: -157px;
}
.tr {
	top: -300px;
	right: -125px;
}
.bl {
	bottom: -350px;
	left: -110px;
}
.br {
	bottom: -250px;
	right: -200px;
}

/* Gradients (matches your palette) */
.tl,
.tr {
	background: linear-gradient(#a855f7, #ec4899);
}
.bl,
.br {
	background: linear-gradient(#3b82f6, #06b6d4);
}

/* Keep content above blobs */
.content {
	position: relative;
	z-index: 1;
	text-align: center;
}
.accent {
	color: #a855f7;
}

/* Responsive tweaks */
@media (max-width: 480px) {
	.tr,
	.br {
		display: none;
	}
	.blob {
		width: 420px;
		height: 420px;
		filter: blur(150px);
	}
}
</style>
