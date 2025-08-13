<template>
  <main class="app-shell">
    <Sidebar
      :active="activeItem"
      :avatar="avatarUrl"
      @new-recording="handleNew"
      @search="handleSearch"
    />

    <section class="content">
      <div class="hero">
        <FontAwesomeIcon :icon="faMicrophoneLines" class="mic" />
        <h2>Let’s get started, Zhi!</h2>
      </div>
    </section>
  </main>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import Sidebar from '@/components/Sidebar.vue'
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
import { faMicrophoneLines } from '@fortawesome/free-solid-svg-icons'

const router = useRouter()
const activeItem = ref('new')                 // set based on current view

function handleNew()      { activeItem.value = 'new'; /* open recorder */ }
function handleSearch()   { activeItem.value = 'search'; /* open search UI */ }
function goHistory()      { activeItem.value = 'history'; router.push('/app/history') }
function goSettings()     { activeItem.value = 'settings'; router.push('/app/settings') }
function goProfile()      { router.push('/app/profile') }
</script>

<style lang="scss" scoped>
.app-shell {
  min-height: 100vh;
}

/* push content so it doesn’t sit under the fixed sidebar */
.content {
  margin-left: 64px;
  min-height: 100vh;
  display: grid;
  place-items: center;
  padding: 24px;
}

/* center hero for your initial state */
.hero {
  text-align: center;
}
.mic {
  font-size: 120px;
  color: #111827;
}
</style>
