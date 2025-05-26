// # kurup - A simple, markdown-based note taking application
// # Copyright (C) 2025 Davis Thomas Daniel
// #
// # This file is part of kurup.
// #
// # kurup is free software: you can redistribute it and/or modify
// # it under the terms of the GNU General Public License as published by
// # the Free Software Foundation, either version 3 of the License, or
// # (at your option) any later version.
// #
// # kurup is distributed in the hope that it will be useful,
// # but WITHOUT ANY WARRANTY; without even the implied warranty of
// # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// # GNU General Public License for more details.
// #
// # You should have received a copy of the GNU General Public License
// # along with kurup. If not, see <https://www.gnu.org/licenses/>.

// apply markdown formatting to selected text in a textarea
function formatSelectedText(textareaId, formatType) {
    const textarea = document.querySelector(`#${textareaId} textarea`) || 
                    document.querySelector(`textarea[id="${textareaId}"]`) || 
                    document.querySelector('textarea');
    
    if (!textarea) {
        console.error('Textarea not found');
        return;
    }

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    
    if (start === end) {
        insertFormattingAtCursor(textarea, formatType, start);
        return;
    }

    const selectedText = textarea.value.substring(start, end);
    const before = textarea.value.substring(0, start);
    const after = textarea.value.substring(end);
    
    let formattedText;
    let selectionOffset = 0;
    
    switch (formatType) {
        case 'bold':
            formattedText = `**${selectedText}**`;
            selectionOffset = 4; // Length of '**' + '**'
            break;
        case 'italic':
            formattedText = `*${selectedText}*`;
            selectionOffset = 2;
            break;
        case 'underline':
            formattedText = `<u>${selectedText}</u>`;
            selectionOffset = 7;
            break;
        case 'strikethrough':
            formattedText = `<s>${selectedText}</s>`;
            selectionOffset = 7;
            break;
        case 'h1':
            formattedText = `# ${selectedText}`;
            selectionOffset = 2;
            break;
        case 'h2':
            formattedText = `## ${selectedText}`;
            selectionOffset = 3;
            break;
        case 'h3':
            formattedText = `### ${selectedText}`;
            selectionOffset = 4;
            break;
        case 'code':
            formattedText = `\`\`\`\n${selectedText}\n\`\`\``;
            selectionOffset = 6;
            break;
        default:
            console.error('Unknown format type:', formatType);
            return;
    }
    
    const newValue = before + formattedText + after;
    textarea.value = newValue;
    textarea.focus();
    
    // keep the text selected, should improve later -dtd
    textarea.setSelectionRange(start, end + selectionOffset);
    
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
    textarea.dispatchEvent(new Event('change', { bubbles: true }));
}

// when no text is selected, insert where the cursor is
function insertFormattingAtCursor(textarea, formatType, cursorPos) {
    const before = textarea.value.substring(0, cursorPos);
    const after = textarea.value.substring(cursorPos);
    
    let insertText;
    let newCursorPos;
    
    switch (formatType) {
        case 'bold':
            insertText = '****';
            newCursorPos = cursorPos + 2;
            break;
        case 'italic':
            insertText = '**';
            newCursorPos = cursorPos + 1;
            break;
        case 'underline':
            insertText = '<u></u>';
            newCursorPos = cursorPos + 3;
            break;
        case 'strikethrough':
            insertText = '<s></s>';
            newCursorPos = cursorPos + 3;
            break;
        case 'h1':
            insertText = '# ';
            newCursorPos = cursorPos + 2;
            break;
        case 'h2':
            insertText = '## ';
            newCursorPos = cursorPos + 3;
            break;
        case 'h3':
            insertText = '### ';
            newCursorPos = cursorPos + 4;
            break;
        case 'code':
            insertText = '``````';
            newCursorPos = cursorPos + 3;
            break;
        default:
            return;
    }
    
    const newValue = before + insertText + after;
    textarea.value = newValue;
    textarea.focus();
    textarea.setSelectionRange(newCursorPos, newCursorPos);
    
    textarea.dispatchEvent(new Event('input', { bubbles: true }));
    textarea.dispatchEvent(new Event('change', { bubbles: true }));
}

//  if present, remove formatting
function removeFormatting(textareaId, formatType) {
    const textarea = document.querySelector(`#${textareaId} textarea`) || 
                    document.querySelector(`textarea[id="${textareaId}"]`) || 
                    document.querySelector('textarea');
    
    if (!textarea) {
        console.error('Textarea not found');
        return;
    }

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    
    if (start === end) return; // No text selected
    
    const selectedText = textarea.value.substring(start, end);
    const before = textarea.value.substring(0, start);
    const after = textarea.value.substring(end);
    
    let cleanedText = selectedText;
    let lengthDiff = 0;
    
    switch (formatType) {
        case 'bold':
            cleanedText = selectedText.replace(/^\*\*(.*)\*\*$/, '$1');
            lengthDiff = selectedText.length - cleanedText.length;
            break;
        case 'italic':
            cleanedText = selectedText.replace(/^\*(.*)\*$/, '$1');
            lengthDiff = selectedText.length - cleanedText.length;
            break;
        case 'underline':
            cleanedText = selectedText.replace(/^<u>(.*)<\/u>$/, '$1');
            lengthDiff = selectedText.length - cleanedText.length;
            break;
        case 'strikethrough':
            cleanedText = selectedText.replace(/^<s>(.*)<\/s>$/s, '$1');
            lengthDiff = selectedText.length - cleanedText.length;
            break;
        case 'h1':
            cleanedText = selectedText.replace(/^# (.*)$/s, '$1');
            lengthDiff = selectedText.length - cleanedText.length;
            break;
        case 'h2':
            cleanedText = selectedText.replace(/^## (.*)$/s, '$1');
            lengthDiff = selectedText.length - cleanedText.length;
            break;
        case 'h3':
            cleanedText = selectedText.replace(/^### (.*)$/s, '$1');
            lengthDiff = selectedText.length - cleanedText.length;
            break;
        case 'code':
            cleanedText = selectedText.replace(/^```(?:\w*\n)?([\s\S]*?)\n?```$/s, '$1');
            lengthDiff = selectedText.length - cleanedText.length;
            break;
    }
    
    if (lengthDiff > 0) {
        const newValue = before + cleanedText + after;
        textarea.value = newValue;
        textarea.focus();
        textarea.setSelectionRange(start, end - lengthDiff);
        
        textarea.dispatchEvent(new Event('input', { bubbles: true }));
        textarea.dispatchEvent(new Event('change', { bubbles: true }));
    }
}

// apply if not present, remove if present, formatting toggle

function toggleFormatting(textareaId, formatType) {
    const textarea = document.querySelector(`#${textareaId} textarea`) || 
                    document.querySelector(`textarea[id="${textareaId}"]`) || 
                    document.querySelector('textarea');
    
    if (!textarea) {
        console.error('Textarea not found');
        return;
    }

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    
    if (start === end) {
        insertFormattingAtCursor(textarea, formatType, start);
        return;
    }
    
    const selectedText = textarea.value.substring(start, end);
    
    let isFormatted = false;
    switch (formatType) {
        case 'bold':
            isFormatted = /^\*\*.*\*\*$/s.test(selectedText);
            break;
        case 'italic':
            isFormatted = /^\*.*\*$/s.test(selectedText) && !/^\*\*.*\*\*$/s.test(selectedText);
            break;
        case 'underline':
            isFormatted = /^<u>.*<\/u>$/s.test(selectedText);
            break;
        case 'strikethrough':
            isFormatted = /^<s>.*<\/s>$/s.test(selectedText);
            break;
        case 'h1':
            isFormatted = /^# .*$/s.test(selectedText);
            break;
        case 'h2':
            isFormatted = /^## .*$/s.test(selectedText);
            break;
        case 'h3':
            isFormatted = /^### .*$/s.test(selectedText);
            break;
        case 'code':
            isFormatted = /^```(?:\w*\n)?[\s\S]*?\n?```$/s.test(selectedText);
            break;
    }
    
    if (isFormatted) {
        removeFormatting(textareaId, formatType);
    } else {
        formatSelectedText(textareaId, formatType);
    }
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    if (e.target.tagName.toLowerCase() !== 'textarea') return;
    
    if (e.ctrlKey || e.metaKey) {
        switch (e.key.toLowerCase()) {
            case 'b':
                e.preventDefault();
                toggleFormatting(e.target.id || 'noteTextarea', 'bold');
                break;
            case 'i':
                e.preventDefault();
                toggleFormatting(e.target.id || 'noteTextarea', 'italic');
                break;
            case 'u':
                e.preventDefault();
                toggleFormatting(e.target.id || 'noteTextarea', 'underline');
                break;
        }
    }
});

window.formatSelectedText = formatSelectedText;
window.removeFormatting = removeFormatting;
window.toggleFormatting = toggleFormatting;