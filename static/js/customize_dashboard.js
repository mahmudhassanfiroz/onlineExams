
document.addEventListener('DOMContentLoaded', function() {
    const layoutSelect = document.getElementById('layout');
    const colorSchemeSelect = document.getElementById('color_scheme');
    const widgetOrder = document.getElementById('widget-order');
    const widgetOrderInput = document.getElementById('widget_order_input');
    const previewContainer = document.getElementById('layout-preview-container');

    function updatePreview() {
        const layout = layoutSelect.value;
        const colorScheme = colorSchemeSelect.value;
        previewContainer.className = `preview-${layout} ${colorScheme}`;
        previewContainer.innerHTML = `<div class="preview-content">
            <h5>লেআউট: ${layout}</h5>
            <h5>কালার স্কিম: ${colorScheme}</h5>
            <p>উইজেট অর্ডার:</p>
            <ul>
                ${Array.from(widgetOrder.children).map(item => `<li>${item.textContent}</li>`).join('')}
            </ul>
        </div>`;
    }

    layoutSelect.addEventListener('change', updatePreview);
    colorSchemeSelect.addEventListener('change', updatePreview);

    // ড্র্যাগ-এন্ড-ড্রপ ফাংশনালিটি
    let draggedItem = null;

    widgetOrder.addEventListener('dragstart', function(e) {
        draggedItem = e.target;
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/html', draggedItem.innerHTML);
    });

    widgetOrder.addEventListener('dragover', function(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';
    });

    widgetOrder.addEventListener('drop', function(e) {
        e.preventDefault();
        const target = e.target.closest('.list-group-item');
        if (target && target !== draggedItem) {
            if (target.nextSibling === draggedItem) {
                target.parentNode.insertBefore(draggedItem, target);
            } else {
                target.parentNode.insertBefore(draggedItem, target.nextSibling);
            }
            updateWidgetOrder();
            updatePreview();
        }
    });

    function updateWidgetOrder() {
        const order = Array.from(widgetOrder.children).map(item => item.dataset.widget);
        widgetOrderInput.value = order.join(',');
    }

    updateWidgetOrder();
    updatePreview();

    // ফর্ম সাবমিশন
    document.getElementById('customizationForm').addEventListener('submit', function(e) {
        updateWidgetOrder();
    });
});
