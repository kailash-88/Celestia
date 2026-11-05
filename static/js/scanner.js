(function () {
  const input = document.getElementById('image');
  if (!input) return;
  const previewWrap = document.getElementById('previewWrap');
  const previewImg = document.getElementById('previewImg');
  const removeBtn = document.getElementById('removeImg');
  if (!previewWrap || !previewImg) return;

  input.addEventListener('change', function () {
    const file = input.files && input.files[0];
    if (!file) { previewWrap.style.display = 'none'; return; }
    const reader = new FileReader();
    reader.onload = function (e) { previewImg.src = e.target.result; previewWrap.style.display = 'block'; };
    reader.readAsDataURL(file);
  });

  if (removeBtn) {
    removeBtn.addEventListener('click', function () {
      input.value = '';
      previewImg.src = '';
      previewWrap.style.display = 'none';
    });
  }
})();
