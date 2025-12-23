let billItems = [];
let shopSettings = { currency_symbol: '$', default_tax_rate: 0 };

document.addEventListener('DOMContentLoaded', loadSettings);

async function loadSettings() {
    try {
        const response = await fetch('/api/settings');
        if (response.ok) {
            shopSettings = await response.json();
            const symbolFunction = (s) => document.querySelectorAll('#currencySymbol, #totalCurrency').forEach(el => el.textContent = s);
            symbolFunction(shopSettings.currency_symbol);

            document.getElementById('taxRate').value = shopSettings.default_tax_rate;
            // Initial update
            updateTotals();
        }
    } catch (e) { console.error('Error loading settings', e); }
}

function handleEnter(e) {
    if (e.key === 'Enter') {
        searchProduct();
    }
}

async function searchProduct() {
    const query = document.getElementById('productSearch').value;
    if (!query) return;

    try {
        // Try exact barcode match first
        let response = await fetch(`/api/product/${query}`);
        if (response.ok) {
            const product = await response.json();
            addItemToBill(product);
            document.getElementById('productSearch').value = '';
            document.getElementById('searchResults').innerHTML = '';
            return;
        }

        // Fallback to name search
        response = await fetch(`/api/products?q=${query}`);
        const products = await response.json();
        displaySearchResults(products);

    } catch (e) {
        console.error('Error searching:', e);
    }
}

function displaySearchResults(products) {
    const container = document.getElementById('searchResults');
    container.innerHTML = '';

    if (products.length === 0) {
        container.innerHTML = '<p style="padding:10px;">No products found.</p>';
        return;
    }

    const list = document.createElement('div');
    products.forEach(p => {
        const item = document.createElement('div');
        item.style.padding = '10px';
        item.style.borderBottom = '1px solid #eee';
        item.style.cursor = 'pointer';
        item.style.display = 'flex';
        item.style.justifyContent = 'space-between';

        item.innerHTML = `
            <span>${p.name}</span> 
            <span style="font-weight:bold">${shopSettings.currency_symbol}${p.price}</span>`;

        item.onclick = () => {
            addItemToBill(p);
            container.innerHTML = '';
            document.getElementById('productSearch').value = '';
        };
        list.appendChild(item);
    });
    container.appendChild(list);
}

function addItemToBill(product) {
    const existingItem = billItems.find(i => i.product_id === product.id);
    if (existingItem) {
        existingItem.quantity++;
        existingItem.subtotal = existingItem.quantity * existingItem.price;
    } else {
        billItems.push({
            product_id: product.id,
            name: product.name,
            price: product.price,
            quantity: 1,
            subtotal: product.price
        });
    }
    renderBill();
}

function removeItem(index) {
    billItems.splice(index, 1);
    renderBill();
}

function updateQuantity(index, delta) {
    const item = billItems[index];
    item.quantity += delta;
    if (item.quantity <= 0) {
        removeItem(index);
        return;
    }
    item.subtotal = item.quantity * item.price;
    renderBill();
}

function renderBill() {
    const tbody = document.querySelector('#billTable tbody');
    tbody.innerHTML = '';
    let subtotal = 0;

    billItems.forEach((item, index) => {
        subtotal += item.subtotal;
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td>${item.name}</td>
            <td>${shopSettings.currency_symbol}${item.price.toFixed(2)}</td>
            <td>
                <button onclick="updateQuantity(${index}, -1)" class="btn btn-sm btn-secondary" style="padding: 2px 8px;">-</button>
                <span style="margin:0 8px">${item.quantity}</span>
                <button onclick="updateQuantity(${index}, 1)" class="btn btn-sm btn-secondary" style="padding: 2px 8px;">+</button>
            </td>
            <td>${shopSettings.currency_symbol}${item.subtotal.toFixed(2)}</td>
            <td><button onclick="removeItem(${index})" class="btn btn-sm btn-danger" style="padding: 2px 8px;">&times;</button></td>
        `;
        tbody.appendChild(tr);
    });

    document.getElementById('subtotalAmount').textContent = subtotal.toFixed(2);
    updateTotals(subtotal);
}

function updateTotals(subtotalOverride) {
    let subtotal = subtotalOverride;
    if (subtotal === undefined) {
        subtotal = parseFloat(document.getElementById('subtotalAmount').textContent || 0);
    }

    const taxRate = parseFloat(document.getElementById('taxRate').value) || 0;
    const discountAmount = parseFloat(document.getElementById('discountAmount').value) || 0;

    const taxAmount = subtotal * (taxRate / 100);
    const total = subtotal + taxAmount - discountAmount;

    document.getElementById('taxAmountDisplay').textContent = taxAmount.toFixed(2);
    document.getElementById('totalAmount').textContent = Math.max(0, total).toFixed(2);
}

async function processCheckout() {
    if (billItems.length === 0) {
        alert('Bill is empty!');
        return;
    }

    const customerName = document.getElementById('customerName').value;
    const subtotal = parseFloat(document.getElementById('subtotalAmount').textContent);
    const taxAmount = parseFloat(document.getElementById('taxAmountDisplay').textContent);
    const discountAmount = parseFloat(document.getElementById('discountAmount').value) || 0;
    const totalAmount = parseFloat(document.getElementById('totalAmount').textContent);
    const paymentMode = document.getElementById('paymentMode').value;

    const payload = {
        customer_name: customerName,
        subtotal: subtotal,
        tax_amount: taxAmount,
        discount_amount: discountAmount,
        total_amount: totalAmount,
        payment_mode: paymentMode,
        items: billItems
    };

    try {
        const response = await fetch('/api/checkout', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        if (response.ok) {
            const result = await response.json();
            // Ask to print
            if (confirm('Sale Complete! Print Receipt?')) {
                window.open(`/receipt/${result.bill_id}`, '_blank', 'width=400,height=600');
            }

            // Reset
            billItems = [];
            renderBill();
            document.getElementById('customerName').value = '';
            document.getElementById('discountAmount').value = 0;
        } else {
            const err = await response.json();
            alert('Checkout Failed: ' + err.error);
        }
    } catch (e) {
        console.error(e);
        alert('Network error during checkout');
    }
}
