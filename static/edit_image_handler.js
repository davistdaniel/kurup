// edit area paste handler for kurup
document.addEventListener('DOMContentLoaded', () => {
  // Handle regular textarea (new note)
  const textarea = document.querySelector('textarea#EditNoteTextarea');
  if (textarea) {
    setupPasteHandler(textarea);
  }
  
  const observer = new MutationObserver((mutations) => {
    mutations.forEach((mutation) => {
      if (mutation.addedNodes && mutation.addedNodes.length > 0) {
        mutation.addedNodes.forEach((node) => {
          const textareas = node.querySelectorAll ? node.querySelectorAll('textarea') : [];
          textareas.forEach(textarea => {
            if (!textarea.hasAttribute('data-paste-handler')) {
              setupPasteHandler(textarea);
            }
          });
        });
      }
    });
  });
  
  observer.observe(document.body, { childList: true, subtree: true });
  
  function setupPasteHandler(textarea) {
    textarea.setAttribute('data-paste-handler', 'true');
    
    textarea.addEventListener('paste', async (event) => {
      const items = event.clipboardData?.items;
      if (!items) return;

      for (const item of items) {
        if (item.type.startsWith('image/')) {
          const file = item.getAsFile();
          if (!file) return;

          const formData = new FormData();
          formData.append('file', file);
          
          try {
            const cursorPos = textarea.selectionStart;
            const textBefore = textarea.value.substring(0, cursorPos);
            const textAfter = textarea.value.substring(cursorPos);
            textarea.value = textBefore + "[Uploading image...]" + textAfter;
            
            const response = await fetch('/upload_image', {
              method: 'POST',
              body: formData,
            });
            
            const result = await response.json();
            const imageUrl = result.url;
            
            const markdownSyntax = `![pasted image](${imageUrl})`;
            const newTextBefore = textarea.value.substring(0, cursorPos);
            const newTextAfter = textarea.value.substring(cursorPos + "[Uploading image...]".length);
            textarea.value = newTextBefore + markdownSyntax + newTextAfter;
            
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
          } catch (err) {
            console.error('Image upload failed', err);
            
            // upload failed
            textarea.value = textBefore + "[Image upload failed]" + textAfter;
            textarea.dispatchEvent(new Event('input', { bubbles: true }));
          }
          
          break;
        }
      }
    });
  }
});