// State
let products = [];
let toppings = [];
let storeConfig = {};
let cart = JSON.parse(localStorage.getItem('bitebabe_cart')) || [];

// DOM Elements
const productsGrid = document.getElementById('productsGrid');
const cartOverlay = document.getElementById('cartOverlay');
const cartItemsContainer = document.getElementById('cartItems');
const cartTotalElement = document.getElementById('cartTotal');
const cartBadge = document.getElementById('cartBadge');
const modal = document.getElementById('productModal');
const modalBody = document.getElementById('modalBody');

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
    await loadData();
    renderProducts();
    updateCartUI();
    renderStoreInfo();
});

// Load Data
async function loadData() {
    try {
        const [prodRes, topRes, storeRes] = await Promise.all([
            fetch('data/products.json'),
            fetch('data/toppings.json'),
            fetch('data/store.json')
        ]);

        products = await prodRes.json();
        toppings = await topRes.json();
        storeConfig = await storeRes.json();
    } catch (error) {
        console.error('Error loading data:', error);
        productsGrid.innerHTML = '<p class="error">Failed to load products. Please try again later.</p>';
    }
}

// Render Store Info
function renderStoreInfo() {
    if (storeConfig.name) {
        document.querySelector('.brand-name').textContent = storeConfig.name;
        document.title = storeConfig.name;
    }
    if (storeConfig.slogan) {
        document.querySelector('.hero-subtitle').textContent = storeConfig.slogan;
    }
}

// Render Products
function renderProducts() {
    productsGrid.innerHTML = products.map(product => `
        <div class="product-card">
            <img src="${product.image}" alt="${product.name}" class="product-image" onerror="this.src='https://placehold.co/400x400/FFD6E8/FF5C9E?text=Cookie'">
            <div class="product-info">
                <div class="product-category">${product.category}</div>
                <h3 class="product-title">${product.name}</h3>
                <div class="product-price">${formatRupiah(product.price)}</div>
                <button class="btn btn-primary btn-block" onclick="openProductModal('${product.id}')">
                    Add to Cart
                </button>
            </div>
        </div>
    `).join('');
}

// Product Modal
function openProductModal(productId) {
    const product = products.find(p => p.id === productId);
    if (!product) return;

    const productToppings = toppings.filter(t => product.toppings.includes(t.id));

    modalBody.innerHTML = `
        <div style="text-align: center; margin-bottom: 20px;">
            <img src="${product.image}" style="width: 150px; height: 150px; object-fit: cover; border-radius: 10px; margin-bottom: 10px;" onerror="this.src='https://placehold.co/400x400/FFD6E8/FF5C9E?text=Cookie'">
            <h2>${product.name}</h2>
            <p style="color: var(--text-light);">${product.description}</p>
            <h3 style="color: var(--accent); margin-top: 10px;">${formatRupiah(product.price)}</h3>
        </div>

        <div class="form-group">
            <label>Quantity</label>
            <div style="display: flex; align-items: center; gap: 10px; justify-content: center; margin-bottom: 20px;">
                <button class="qty-btn" onclick="adjustModalQty(-1)">-</button>
                <span id="modalQty" style="font-weight: bold; font-size: 1.2rem;">1</span>
                <button class="qty-btn" onclick="adjustModalQty(1, ${product.max_order})">+</button>
            </div>
        </div>

        ${productToppings.length > 0 ? `
            <div class="form-group">
                <label>Extra Toppings</label>
                <div class="toppings-list">
                    ${productToppings.map(t => `
                        <label class="topping-option">
                            <span>${t.name}</span>
                            <span>+${formatRupiah(t.price)}</span>
                            <input type="checkbox" value="${t.id}" data-price="${t.price}" data-name="${t.name}" onchange="toggleToppingSelection('${t.id}', this)">
                        </label>
                    `).join('')}
                </div>
            </div>
        ` : ''}

        <button class="btn btn-primary btn-block" onclick="addToCart('${product.id}')">
            Add to Order - <span id="modalTotal">${formatRupiah(product.price)}</span>
        </button>
    `;

    modal.classList.add('active');
    window.currentModalProduct = product;
    window.currentModalQty = 1;
    window.currentModalToppings = [];
}

function closeModal() {
    modal.classList.remove('active');
}

function adjustModalQty(delta, max) {
    let newQty = window.currentModalQty + delta;
    if (newQty < 1) newQty = 1;
    if (max && newQty > max) newQty = max;

    window.currentModalQty = newQty;
    document.getElementById('modalQty').textContent = newQty;
    updateModalTotal();
}

function toggleToppingSelection(toppingId, checkboxElement) {
    // Toggle selected class on parent label
    const label = checkboxElement.closest('.topping-option');
    if (checkboxElement.checked) {
        label.classList.add('selected');
    } else {
        label.classList.remove('selected');
    }

    const topping = toppings.find(t => t.id === toppingId);
    if (checkboxElement.checked) {
        window.currentModalToppings.push(topping);
    } else {
        window.currentModalToppings = window.currentModalToppings.filter(t => t.id !== toppingId);
    }
    updateModalTotal();
}

function updateModalTotal() {
    const basePrice = window.currentModalProduct.price;
    const toppingsPrice = window.currentModalToppings.reduce((sum, t) => sum + t.price, 0);
    const total = (basePrice + toppingsPrice) * window.currentModalQty;
    document.getElementById('modalTotal').textContent = formatRupiah(total);
}

// Cart Logic
function addToCart(productId) {
    const product = products.find(p => p.id === productId);
    const cartItem = {
        id: Date.now(), // Unique ID for cart item
        productId: product.id,
        name: product.name,
        price: product.price,
        image: product.image,
        qty: window.currentModalQty,
        toppings: [...window.currentModalToppings]
    };

    cart.push(cartItem);
    saveCart();
    closeModal();
    toggleCart(); // Open cart to show item added
}

function removeFromCart(cartItemId) {
    cart = cart.filter(item => item.id !== cartItemId);
    saveCart();
}

function updateCartQty(cartItemId, delta) {
    const item = cart.find(i => i.id === cartItemId);
    if (!item) return;

    const product = products.find(p => p.id === item.productId);
    let newQty = item.qty + delta;

    if (newQty < 1) {
        removeFromCart(cartItemId);
        return;
    }
    if (product.max_order && newQty > product.max_order) return;

    item.qty = newQty;
    saveCart();
}

function saveCart() {
    localStorage.setItem('bitebabe_cart', JSON.stringify(cart));
    updateCartUI();
}

function updateCartUI() {
    cartBadge.textContent = cart.reduce((sum, item) => sum + item.qty, 0);

    if (cart.length === 0) {
        cartItemsContainer.innerHTML = '<div class="empty-cart">Your cart is empty.</div>';
        cartTotalElement.textContent = formatRupiah(0);
        return;
    }

    let total = 0;
    cartItemsContainer.innerHTML = cart.map(item => {
        const toppingsPrice = item.toppings.reduce((sum, t) => sum + t.price, 0);
        const itemTotal = (item.price + toppingsPrice) * item.qty;
        total += itemTotal;

        return `
            <div class="cart-item">
                <img src="${item.image}" class="cart-item-img" onerror="this.src='https://placehold.co/100x100/FFD6E8/FF5C9E?text=Cookie'">
                <div class="cart-item-details">
                    <div class="cart-item-title">${item.name}</div>
                    <div class="cart-item-price">${formatRupiah(item.price)}</div>
                    ${item.toppings.length ? `
                        <div class="cart-item-toppings">
                            + ${item.toppings.map(t => t.name).join(', ')}
                        </div>
                    ` : ''}
                    <div class="cart-controls">
                        <button class="qty-btn" onclick="updateCartQty(${item.id}, -1)">-</button>
                        <span>${item.qty}</span>
                        <button class="qty-btn" onclick="updateCartQty(${item.id}, 1)">+</button>
                        <button class="remove-btn" onclick="removeFromCart(${item.id})"><i class="fa-solid fa-trash"></i></button>
                    </div>
                </div>
            </div>
        `;
    }).join('');

    cartTotalElement.textContent = formatRupiah(total);
}

function toggleCart() {
    cartOverlay.classList.toggle('active');
}

// Checkout
function checkoutWhatsApp() {
    if (cart.length === 0) {
        alert('Your cart is empty!');
        return;
    }

    const name = document.getElementById('customerName').value;
    const address = document.getElementById('customerAddress').value;
    const payment = document.getElementById('paymentMethod').value;

    if (!name || !address) {
        alert('Please fill in your name and address.');
        return;
    }

    let message = `Halo, saya ingin pesan:\n\n`;
    let total = 0;

    cart.forEach(item => {
        const toppingsPrice = item.toppings.reduce((sum, t) => sum + t.price, 0);
        const itemTotal = (item.price + toppingsPrice) * item.qty;
        total += itemTotal;

        message += `🍪 ${item.name} x${item.qty} — ${formatRupiah(itemTotal)}\n`;
        if (item.toppings.length) {
            message += `   + Topping: ${item.toppings.map(t => t.name).join(', ')}\n`;
        }
        message += `\n`;
    });

    message += `Total: ${formatRupiah(total)}\n\n`;
    message += `Nama: ${name}\n`;
    message += `Alamat: ${address}\n`;
    message += `Metode Pembayaran: ${payment}`;

    const whatsappNumber = storeConfig.whatsapp || '628123456789';
    const url = `https://wa.me/${whatsappNumber}?text=${encodeURIComponent(message)}`;

    window.open(url, '_blank');
}

// Utility
function formatRupiah(number) {
    return new Intl.NumberFormat('id-ID', {
        style: 'currency',
        currency: 'IDR',
        minimumFractionDigits: 0
    }).format(number);
}
