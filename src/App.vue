<script setup lang="ts">
import { RouterView } from 'vue-router'
import AppFooter from './components/AppFooter.vue'
</script>

<template>
  <div class="app-layout">
    <main class="app-main">
      <RouterView />
    </main>
    <AppFooter />
  </div>
</template>

<style>
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
  background-color: #f9f7f2;
  color: #2b4c24;
  -webkit-font-smoothing: antialiased;
}

.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
}

.card {
  background-color: #ffffff;
  border: 1.5px solid #2b4c24;
  border-radius: 24px;
  padding: 32px;
  width: 100%;
  max-width: 540px;
  margin: 24px 16px;
  box-shadow: 0 10px 30px rgba(43, 76, 36, 0.05);
}

.btn-primary {
  background-color: #26481c;
  color: #ffffff;
  border: none;
  border-radius: 999px;
  padding: 14px 32px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s ease, transform 0.1s ease;
  width: 100%;
}

.btn-primary:hover {
  background-color: #1d3815;
}

.btn-primary:active {
  transform: scale(0.99);
}

@media (max-width: 600px) {
  .card {
    padding: 24px 16px;
    border-radius: 20px;
  }
}
</style>