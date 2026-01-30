

let lastCheckedIndex = null;

function save_item() {
    window.location.href = "/save_grocery_item/";
}

function delete_n_upload() {
    window.location.href = "/delete_all_Grocery_TEMP_Items/";
}    

function guessLabelForNewItems() {
    window.location.href = "/guess_label_for_new_items/";
}

 function fake_populate_all() {
    window.location.href = "/fake_populate_all/";
}

function lastUpload() {
    window.location.href = "/last_upload/";
}

function updateDate() {
    window.location.href = "/update_date/";
}

function deleteSelected() { /*deleteSelected code was written by Claud AI*/
    const checkboxes = document.querySelectorAll('input[name="item_ids"]:checked');
    if (checkboxes.length === 0) {
        alert('Please select at least one item to delete');
        return;
    }

    const ids = Array.from(checkboxes).map(cb => cb.value);
    const confirmation = confirm(`Are you sure you want to delete ${ids.length} item(s)?`);

    if (confirmation) {
        // Create a form and submit
        const form = document.createElement('form');
        form.method = 'POST';
        form.action = '/delete_multiple_items_TempDB/';

        ids.forEach(id => {
            const input = document.createElement('input');
            input.type = 'hidden';
            input.name = 'item_ids';
            input.value = id;
            form.appendChild(input);
        });

        document.body.appendChild(form);
        form.submit();
    }
}

function toggleAll(source) {
    const checkboxes = document.querySelectorAll('input[name="item_ids"]');
    checkboxes.forEach(cb => cb.checked = source.checked);
    lastCheckedIndex = null;
}

function handleCheckboxClick(event, currentIndex) {
    const checkboxes = document.querySelectorAll('input[name="item_ids"]');

    if (event.shiftKey && lastCheckedIndex !== null) {
        // Determine range
        const start = Math.min(lastCheckedIndex, currentIndex);
        const end = Math.max(lastCheckedIndex, currentIndex);

        // Check all checkboxes in range
        const isChecked = checkboxes[currentIndex].checked;
        for (let i = start; i <= end; i++) {
            checkboxes[i].checked = isChecked;
        }
    }

    lastCheckedIndex = currentIndex;
}

function openImageModal() {
    const modal = document.getElementById("receiptModal");
    const container = document.getElementById("modalContainer");
    modal.style.display = "block";
    // Reset position when opening
    container.style.left = '0px';
    container.style.top = '0px';
}

function closeImageModal() {
    document.getElementById("receiptModal").style.display = "none";
}

function closeDateWarning() {
    document.getElementById('dateWarningModal').style.display = 'none';
}

// Panning functionality
let isDragging = false;
let startX, startY;

document.addEventListener('DOMContentLoaded', function() {
    const modal = document.getElementById("receiptModal");
    const container = document.getElementById("modalContainer");
    const closeBtn = document.getElementById("closeBtn");

    modal.addEventListener('mousedown', function(e) {
        if (e.target === closeBtn) return;
        isDragging = true;
        modal.classList.add('grabbing');
        startX = e.pageX - container.offsetLeft;
        startY = e.pageY - container.offsetTop;
    });

    modal.addEventListener('mousemove', function(e) {
        if (!isDragging) return;
        e.preventDefault();
        const x = e.pageX - startX;
        const y = e.pageY - startY;
        container.style.left = x + 'px';
        container.style.top = y + 'px';
    });

    modal.addEventListener('mouseup', function() {
        isDragging = false;
        modal.classList.remove('grabbing');
    });

    modal.addEventListener('mouseleave', function() {
        isDragging = false;
        modal.classList.remove('grabbing');
    });

    // Close on ESC key
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && modal.style.display === 'block') {
            closeImageModal();
        }
    });

});

// Close date warning when clicking outside
window.onclick = function(event) {
    var modal = document.getElementById('dateWarningModal');
    if (event.target == modal) {
        modal.style.display = 'none';
    }
}
