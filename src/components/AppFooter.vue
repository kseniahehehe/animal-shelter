<script setup lang="ts">

</script>

<template>
  <footer class="site-footer">
    <div class="footer-container">
      <div class="footer-content">
        <span class="footer-item">© 2026 Благотворительный фонд помощи бездомным животным «Ника»</span>
        <a href="mailto:info@fond-nika.ru" class="footer-link">info@fond-nika.ru</a>
        <a href="tel:+74951628595" class="footer-link">+7 (495) 162-85-95</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  width: 100%;
  background-color: #f6f7f2;
  padding: 0 24px 32px;
  box-sizing: border-box;
  margin-top: auto;
}

.footer-container {
  max-width: 1240px;
  margin: 0 auto;
  border-top: 1px solid #e2e4db;
  padding-top: 20px;
}

.footer-content {
  display: flex;
  justify-content: center;
  align-items: center;
  text-align: center;
  flex-wrap: wrap;
  gap: 12px 28px;
  font-size: 13px;
  color: #7c8277;
}

.footer-link {
  color: #7c8277;
  text-decoration: none;
  transition: color 0.15s ease;
}

.footer-link:hover {
  color: #1f241d;
}

@media (max-width: 600px) {
  .site-footer {
    padding: 0 16px 24px;
  }

  .footer-content {
    flex-direction: column;
    align-items: center;
    text-align: center;
    gap: 8px;
    font-size: 12px;
  }
}
</style>