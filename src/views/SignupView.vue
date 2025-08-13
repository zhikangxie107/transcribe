<template>
	<section class="signup">
		<!-- Background -->
		<div class="blob tl"></div>
		<div class="blob tr"></div>
		<div class="blob bl"></div>
		<div class="blob br"></div>

		<div class="content">
			<div class="card">
				<h1 class="title">Sign Up</h1>
				<p class="subtitle">Welcome! Glad to have you</p>

				<form class="form" @submit.prevent="onSubmit">
					<label class="sr-only" for="username">Username</label>
					<input
						id="username"
						v-model="username"
						type="username"
						placeholder="username"
						required
					/>
					<label class="sr-only" for="email">Email</label>
					<input
						id="email"
						v-model="email"
						type="email"
						placeholder="email"
						required
					/>

					<label class="sr-only" for="password">Password</label>
					<input
						id="password"
						v-model="password"
						type="password"
						placeholder="password"
						required
					/>

					<label class="sr-only" for="confirm">Confirm password</label>
					<input
						id="confirm"
						v-model="confirm"
						type="confirm"
						placeholder="confirm password"
						required
					/>

					<button class="btn-primary" :disabled="loading">
						{{ loading ? 'Creating account…' : 'Sign Up' }}
					</button>
				</form>

				<p class="switch">
					Have an account?
					<router-link class="link" to="/login">Login</router-link>
				</p>
			</div>
		</div>
	</section>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
// import { Auth } from '@/client/auth' // when your API is ready

const router = useRouter();
const username = ref('');
const email = ref('');
const password = ref('');
const confirm = ref('');
const loading = ref(false);

async function onSubmit() {
	if (password.value !== confirm.value) {
		alert('Passwords do not match.');
		return;
	}
	try {
		loading.value = true;
		// await Auth.signup({ username: username.value, email: email.value, password: password.value })
		// Optionally auto-login then:
		router.push('/app');
	} catch (err) {
		alert(err?.message || 'Sign up failed');
	} finally {
		loading.value = false;
	}
}
</script>

<style lang="scss" scoped>
@use '@/assets/styles.scss' as *;

.signup {
	position: relative;
	min-height: 100vh;
	display: grid;
	place-items: center;
	overflow: hidden;
}

.card {
	min-width: 25rem;
	max-width: 30rem;
	background: #fff4f4; /* soft blush */
	border: 1px solid rgba(0, 0, 0, 0.08);
	border-radius: 24px;
	padding: 2.25rem 2rem;
	box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
}

/* Headings */
.title {
	margin: 0 0 0.5rem;
	font-size: 2.25rem;
	line-height: 1.15;
	text-align: center;
	font-weight: bold;
	color: #000;
}

.subtitle {
	margin: 0 0 1.5rem;
	text-align: center;
	color: #636363; /* gray-500 */
	font-size: 1.05rem;
}

/* Form */
.form {
	display: grid;
	gap: 1rem;
	margin-top: 0.5rem;
}

input {
	height: 3.5rem;
	max-width: 25.125rem;
	padding: 0 1rem;
	font-size: 1rem;
	border-radius: 16px;
	border: 2px solid #e5e7eb; /* light border */
	background: #f3f4f6; /* light gray fill */
	color: #111827;
	outline: none;
	transition: border-color 0.15s, box-shadow 0.15s;

	&::placeholder {
		color: #9ca3af;
	}
	&:focus {
		border-color: #ab26a0; /* magenta */
		box-shadow: 0 0 0 4px rgba(171, 38, 160, 0.15);
	}
}

/* Primary CTA */
.btn-primary {
	height: 56px;
	width: 100%;
	border: 2px solid #2b0b29; /* subtle dark outline to match mock */
	border-radius: 16px;
	background: #ab26a0; /* magenta */
	color: #fff;
	font-weight: 800;
	font-size: 1.35rem;
	cursor: pointer;
	transition: transform 0.06s ease, filter 0.15s ease;

	&:hover {
		filter: brightness(1.05);
	}
	&:active {
		transform: translateY(1px);
	}
	&:disabled {
		opacity: 0.7;
		cursor: not-allowed;
		filter: grayscale(0.2);
	}
}

/* Bottom switch text */
.switch {
	margin-top: 1.25rem;
	text-align: center;
	color: #6b7280;
}

.link {
	color: #ab26a0;
	font-weight: 600;
	text-decoration: none;
}
.link:hover {
	text-decoration: underline;
}

/* Screen reader only labels */
.sr-only {
	position: absolute;
	width: 1px;
	height: 1px;
	padding: 0;
	margin: -1px;
	overflow: hidden;
	clip: rect(0, 0, 0, 0);
	white-space: nowrap;
	border: 0;
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
