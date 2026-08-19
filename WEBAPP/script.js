 /* =====================================================
   HISOBCHI AI — MINI APP
   ===================================================== */

const tg = window.Telegram?.WebApp || null;


/* =====================================================
   TELEGRAM
   ===================================================== */

if (tg) {
    tg.ready();
    tg.expand();
}


/* =====================================================
   DATA
   ===================================================== */

let data = {
    balance: 0,
    income: 0,
    expense: 0,

    products: [
        {
            name: "Shaik 10ml",
            category: "Shaik",
            price: 0,
            quantity: 0
        },
        {
            name: "Clive & Keira 30ml",
            category: "Clive & Keira",
            price: 0,
            quantity: 0
        }
    ],

    transactions: [],
    clients: []
};


/* =====================================================
   HELPERS
   ===================================================== */

function formatMoney(value) {

    return Number(value || 0)
        .toLocaleString("uz-UZ") + " so'm";

}


function updateBalance() {

    data.balance = data.income - data.expense;

    const balance = document.getElementById("balance");
    const income = document.getElementById("income");
    const expense = document.getElementById("expense");

    if (balance) {
        balance.textContent = formatMoney(data.balance);
    }

    if (income) {
        income.textContent = formatMoney(data.income);
    }

    if (expense) {
        expense.textContent = formatMoney(data.expense);
    }
}


function showMessage(text) {

    alert(text);

}


/* =====================================================
   HOME
   ===================================================== */

function showHome() {

    const app = document.getElementById("app");

    app.innerHTML = `

        <header class="header">

            <div>
                <div class="logo">
                    Hisobchi AI
                </div>

                <div class="subtitle">
                    Biznesingiz nazorat ostida
                </div>
            </div>

            <button class="avatar"
                    onclick="showMessage('Profil')">
                👤
            </button>

        </header>


        <section class="balance-card">

            <div class="balance-title">
                Umumiy balans
            </div>

            <div id="balance" class="balance">
                0 so'm
            </div>

            <div class="balance-row">

                <div>
                    <span>Kirim</span>
                    <strong id="income">
                        0 so'm
                    </strong>
                </div>

                <div>
                    <span>Chiqim</span>
                    <strong id="expense">
                        0 so'm
                    </strong>
                </div>

            </div>

        </section>


        <section class="section">

            <h2>
                Tezkor amallar
            </h2>

            <div class="quick-grid">

                <button class="action income"
                        onclick="openTransaction('income')">

                    <span>＋</span>
                    <small>Kirim</small>

                </button>


                <button class="action expense"
                        onclick="openTransaction('expense')">

                    <span>－</span>
                    <small>Chiqim</small>

                </button>


                <button class="action"
                        onclick="openPage('products')">

                    <span>📦</span>
                    <small>Mahsulotlar</small>

                </button>


                <button class="action"
                        onclick="openPage('reports')">

                    <span>📊</span>
                    <small>Hisobot</small>

                </button>

            </div>

        </section>


        <section class="section">

            <h2>
                Boshqaruv
[17.08.2026 13:04] Азизжон: </h2>

            <div class="menu">

                <button onclick="openPage('products')">

                    <span class="menu-icon">
                        📦
                    </span>

                    <div>
                        <strong>
                            Mahsulotlar
                        </strong>

                        <small>
                            Ombor va mahsulotlar
                        </small>
                    </div>

                    <span class="arrow">›</span>

                </button>


                <button onclick="openPage('transactions')">

                    <span class="menu-icon">
                        💰
                    </span>

                    <div>
                        <strong>
                            Kirim / Chiqim
                        </strong>

                        <small>
                            Moliyaviy harakatlar
                        </small>
                    </div>

                    <span class="arrow">›</span>

                </button>


                <button onclick="openPage('clients')">

                    <span class="menu-icon">
                        👥
                    </span>

                    <div>
                        <strong>
                            Mijozlar
                        </strong>

                        <small>
                            Mijozlar bazasi
                        </small>
                    </div>

                    <span class="arrow">›</span>

                </button>


                <button onclick="openPage('reports')">

                    <span class="menu-icon">
                        📈
                    </span>

                    <div>
                        <strong>
                            Hisobotlar
                        </strong>

                        <small>
                            Kunlik va oylik natijalar
                        </small>
                    </div>

                    <span class="arrow">›</span>

                </button>


                <button onclick="openPage('ai')">

                    <span class="menu-icon">
                        🤖
                    </span>

                    <div>
                        <strong>
                            AI yordamchi
                        </strong>

                        <small>
                            Hisobchi AI
                        </small>
                    </div>

                    <span class="arrow">›</span>

                </button>

            </div>

        </section>


        ${bottomNavigation("home")}

    `;

    updateBalance();
}


/* =====================================================
   BOTTOM NAVIGATION
   ===================================================== */

function bottomNavigation(active) {

    return `

        <nav class="bottom-nav">

            <button
                class="${active === "home" ? "active" : ""}"
                onclick="showHome()">

                <span>🏠</span>
                <small>Bosh sahifa</small>

            </button>


            <button
                class="${active === "products" ? "active" : ""}"
                onclick="openPage('products')">

                <span>📦</span>
                <small>Mahsulotlar</small>

            </button>


            <button
                class="${active === "reports" ? "active" : ""}"
                onclick="openPage('reports')">

                <span>📊</span>
                <small>Hisobot</small>

            </button>


            <button
                class="${active === "settings" ? "active" : ""}"
                onclick="openPage('settings')">

                <span>⚙️</span>
                <small>Sozlamalar</small>

            </button>

        </nav>

    `;
}


/* =====================================================
   PAGE
   ===================================================== */

function openPage(page) {

    if (page === "products") {
        showProducts();
 return;
    }

    if (page === "transactions") {
        showTransactions();
        return;
    }

    if (page === "clients") {
        showClients();
        return;
    }

    if (page === "reports") {
        showReports();
        return;
    }

    if (page === "ai") {
        showAI();
        return;
    }

    if (page === "settings") {
        showSettings();
        return;
    }

}


/* =====================================================
   PRODUCTS
   ===================================================== */

function showProducts() {

    const app = document.getElementById("app");

    let productHTML = "";

    data.products.forEach((product, index) => {

        productHTML += `

            <div class="menu">

                <button onclick="productInfo(${index})">

                    <span class="menu-icon">
                        📦
                    </span>

                    <div>

                        <strong>
                            ${product.name}
                        </strong>

                        <small>
                            ${product.category}
                        </small>

                    </div>

                    <span class="arrow">
                        ›
                    </span>

                </button>

            </div>

        `;

    });


    app.innerHTML = `

        <header class="header">

            <div>

                <div class="logo">
                    📦 Mahsulotlar
                </div>

                <div class="subtitle">
                    Mahsulotlar bazasi
                </div>

            </div>

            <button
                class="avatar"
                onclick="showHome()">

                ←

            </button>

        </header>


        <section class="section">

            <button
                class="action"
                style="width:100%;"
                onclick="addProduct()">

                <span>＋</span>

                <small>
                    Yangi mahsulot
                </small>

            </button>

        </section>


        <section class="section">

            <h2>
                Mahsulotlar
            </h2>

            ${productHTML}

        </section>


        ${bottomNavigation("products")}

    `;

}


/* =====================================================
   PRODUCT INFO
   ===================================================== */

function productInfo(index) {

    const product = data.products[index];

    alert(
        "Mahsulot: " + product.name +
        "\nKategoriya: " + product.category +
        "\nNarx: " + formatMoney(product.price) +
        "\nMiqdor: " + product.quantity
    );

}


/* =====================================================
   ADD PRODUCT
   ===================================================== */

function addProduct() {

    const name = prompt(
        "Mahsulot nomini kiriting:"
    );

    if (!name) {
        return;
    }

    const category = prompt(
        "Kategoriya:"
    ) || "Boshqa";

    const price = Number(
        prompt("Narx:") || 0
    );

    const quantity = Number(
        prompt("Miqdor:") || 0
    );


    data.products.push({

        name,
        category,
        price,
        quantity

    });


    showProducts();

}


/* =====================================================
   TRANSACTION
   ===================================================== */

function openTransaction(type) {

    const title =
        type === "income"
            ? "Kirim summasi:"
            : "Chiqim summasi:";


    const amount = Number(
        prompt(title) || 0
    );


    if (!amount || amount <= 0) {
        return;
    }


    const description =
        prompt("Izoh:") || "";


    const transaction = {

        type,
        amount,
        description,
        date: new Date().toLocaleString("uz-UZ")

    };


    data.transactions.push(transaction);


    if (type === "income") {

        data.income += amount;

    } else {

        data.expense += amount;

    }


    updateBalance();
 alert(
        type === "income"
            ? "Kirim saqlandi ✅"
            : "Chiqim saqlandi ✅"
    );


    showHome();

}


/* =====================================================
   TRANSACTIONS
   ===================================================== */

function showTransactions() {

    const app = document.getElementById("app");


    let html = "";


    if (data.transactions.length === 0) {

        html = `

            <div class="menu">

                <button>

                    <span class="menu-icon">
                        📭
                    </span>

                    <div>

                        <strong>
                            Hozircha operatsiya yo'q
                        </strong>

                        <small>
                            Kirim yoki chiqim qo'shing
                        </small>

                    </div>

                </button>

            </div>

        `;

    } else {

        data.transactions
            .slice()
            .reverse()
            .forEach(item => {

                const icon =
                    item.type === "income"
                        ? "🟢"
                        : "🔴";

                const sign =
                    item.type === "income"
                        ? "+"
                        : "-";


                html += `

                    <div class="menu">

                        <button>

                            <span class="menu-icon">
                                ${icon}
                            </span>

                            <div>

                                <strong>
                                    ${sign}${formatMoney(item.amount)}
                                </strong>

                                <small>
                                    ${item.description || "Izoh yo'q"}
                                    <br>
                                    ${item.date}
                                </small>

                            </div>

                        </button>

                    </div>

                `;

            });

    }


    app.innerHTML = `

        <header class="header">

            <div>

                <div class="logo">
                    💰 Kirim / Chiqim
                </div>

                <div class="subtitle">
                    Moliyaviy operatsiyalar
                </div>

            </div>

            <button
                class="avatar"
                onclick="showHome()">

                ←

            </button>

        </header>


        <section class="section">

            <div class="quick-grid">

                <button
                    class="action income"
                    onclick="openTransaction('income')">

                    <span>＋</span>
                    <small>Kirim</small>

                </button>


                <button
                    class="action expense"
                    onclick="openTransaction('expense')">

                    <span>－</span>
                    <small>Chiqim</small>

                </button>

            </div>

        </section>


        <section class="section">

            <h2>
                Operatsiyalar
            </h2>

            ${html}

        </section>


        ${bottomNavigation("home")}

    `;

}


/* =====================================================
   CLIENTS
   ===================================================== */

function showClients() {

    const app = document.getElementById("app");


    app.innerHTML = `

        <header class="header">

            <div>

                <div class="logo">
                    👥 Mijozlar
                </div>

                <div class="subtitle">
                    Mijozlar bazasi
                </div>

            </div>

            <button
                class="avatar"
                onclick="showHome()">

                ←

            </button>

        </header>


        <section class="section">

            <button
                class="action"
[17.08.2026 13:04] Азизжон: style="width:100%;"
                onclick="addClient()">

                <span>＋</span>

                <small>
                    Yangi mijoz
                </small>

            </button>

        </section>


        <section class="section">

            ${
                data.clients.length === 0

                ?

                `
                <div class="menu">

                    <button>

                        <span class="menu-icon">
                            👤
                        </span>

                        <div>

                            <strong>
                                Mijozlar yo'q
                            </strong>

                            <small>
                                Birinchi mijozni qo'shing
                            </small>

                        </div>

                    </button>

                </div>
                `

                :

                data.clients.map(client => `

                    <div class="menu">

                        <button>

                            <span class="menu-icon">
                                👤
                            </span>

                            <div>

                                <strong>
                                    ${client.name}
                                </strong>

                                <small>
                                    ${client.phone || ""}
                                </small>

                            </div>

                        </button>

                    </div>

                `).join("")

            }

        </section>


        ${bottomNavigation("home")}

    `;

}


/* =====================================================
   ADD CLIENT
   ===================================================== */

function addClient() {

    const name = prompt(
        "Mijoz ismi:"
    );

    if (!name) {
        return;
    }


    const phone = prompt(
        "Telefon:"
    ) || "";


    data.clients.push({

        name,
        phone

    });


    showClients();

}


/* =====================================================
   REPORTS
   ===================================================== */

function showReports() {

    const app = document.getElementById("app");


    app.innerHTML = `

        <header class="header">

            <div>

                <div class="logo">
                    📊 Hisobotlar
                </div>

                <div class="subtitle">
                    Moliyaviy natijalar
                </div>

            </div>

            <button
                class="avatar"
                onclick="showHome()">

                ←

            </button>

        </header>


        <section class="balance-card">

            <div class="balance-title">
                Umumiy balans
            </div>

            <div class="balance">
                ${formatMoney(data.balance)}
            </div>

            <div class="balance-row">

                <div>

                    <span>
                        Jami kirim
                    </span>

                    <strong>
                        ${formatMoney(data.income)}
                    </strong>

                </div>


                <div>

                    <span>
                        Jami chiqim
                    </span>

                    <strong>
                        ${formatMoney(data.expense)}
                    </strong>

                </div>

            </div>

        </section>


        <section class="section">

            <h2>
                Statistika
            </h2>

            <div class="menu">

                <button>

                    <span class="menu-icon">
                        📦
                    </span>

                    <div>

                        <strong>
                            Mahsulotlar
                        </strong>

                        <small>
                            ${data.products.length} ta mahsulot
[17.08.2026 13:04] Азизжон: </small>

                    </div>

                </button>


                <button>

                    <span class="menu-icon">
                        👥
                    </span>

                    <div>

                        <strong>
                            Mijozlar
                        </strong>

                        <small>
                            ${data.clients.length} ta mijoz
                        </small>

                    </div>

                </button>


                <button>

                    <span class="menu-icon">
                        🧾
                    </span>

                    <div>

                        <strong>
                            Operatsiyalar
                        </strong>

                        <small>
                            ${data.transactions.length} ta operatsiya
                        </small>

                    </div>

                </button>

            </div>

        </section>


        ${bottomNavigation("reports")}

    `;

}


/* =====================================================
   AI
   ===================================================== */

function showAI() {

    const app = document.getElementById("app");


    app.innerHTML = `

        <header class="header">

            <div>

                <div class="logo">
                    🤖 Hisobchi AI
                </div>

                <div class="subtitle">
                    Sizning aqlli hisobchingiz
                </div>

            </div>

            <button
                class="avatar"
                onclick="showHome()">

                ←

            </button>

        </header>


        <section class="balance-card">

            <div class="balance-title">
                AI yordamchi
            </div>

            <div class="balance">
                🤖
            </div>

            <div>
                Moliyaviy ma'lumotlaringizni
                tahlil qilishga tayyorman.
            </div>

        </section>


        <section class="section">

            <h2>
                Savol bering
            </h2>


            <div class="menu">

                <button
                    onclick="aiQuestion('Bugungi daromadim qancha?')">

                    <span class="menu-icon">
                        💰
                    </span>

                    <div>

                        <strong>
                            Bugungi daromadim qancha?
                        </strong>

                    </div>

                </button>


                <button
                    onclick="aiQuestion('Qancha chiqim qildim?')">

                    <span class="menu-icon">
                        💸
                    </span>

                    <div>

                        <strong>
                            Qancha chiqim qildim?
                        </strong>

                    </div>

                </button>


                <button
                    onclick="aiQuestion('Balansim qancha?')">

                    <span class="menu-icon">
                        📊
                    </span>

                    <div>

                        <strong>
                            Balansim qancha?
                        </strong>

                    </div>

                </button>

            </div>

        </section>


        ${bottomNavigation("home")}

    `;

}


/* =====================================================
   AI QUESTIONS
   ===================================================== */

function aiQuestion(question) {

    if (
        question.includes("daromad")
    ) {

        alert(
            "Jami kirim: " +
            formatMoney(data.income)
        );

        return;
    }


    if (
        question.includes("chiqim")
    ) {

        alert(
            "Jami chiqim: " +
            formatMoney(data.expense)
        );

        return;
    }


    if (
        question.includes("Balans") ||
        question.includes("balans")
    ) {

        alert(
 "Hozirgi balans: " +
            formatMoney(data.balance)
        );

        return;
    }

}


/* =====================================================
   SETTINGS
   ===================================================== */

function showSettings() {

    const app = document.getElementById("app");


    app.innerHTML = `

        <header class="header">

            <div>

                <div class="logo">
                    ⚙️ Sozlamalar
                </div>

                <div class="subtitle">
                    Hisobchi AI sozlamalari
                </div>

            </div>

            <button
                class="avatar"
                onclick="showHome()">

                ←

            </button>

        </header>


        <section class="section">

            <div class="menu">

                <button
                    onclick="showMessage('Profil sozlamalari')">

                    <span class="menu-icon">
                        👤
                    </span>

                    <div>

                        <strong>
                            Profil
                        </strong>

                        <small>
                            Foydalanuvchi ma'lumotlari
                        </small>

                    </div>

                    <span class="arrow">
                        ›
                    </span>

                </button>


                <button
                    onclick="showMessage('Bildirishnomalar')">

                    <span class="menu-icon">
                        🔔
                    </span>

                    <div>

                        <strong>
                            Bildirishnomalar
                        </strong>

                        <small>
                            Xabarnomalar
                        </small>

                    </div>

                    <span class="arrow">
                        ›
                    </span>

                </button>


                <button
                    onclick="showMessage('Hisobchi AI')">

                    <span class="menu-icon">
                        🤖
                    </span>

                    <div>

                        <strong>
                            Hisobchi AI
                        </strong>

                        <small>
                            AI yordamchi
                        </small>

                    </div>

                    <span class="arrow">
                        ›
                    </span>

                </button>

            </div>

        </section>


        ${bottomNavigation("settings")}

    `;

}


/* =====================================================
   TELEGRAM DATA
   ===================================================== */

function sendDataToBot(dataToSend) {

    if (!tg) {

        console.log(
            "Mini App data:",
            dataToSend
        );

        return;

    }


    try {

        tg.sendData(
            JSON.stringify(dataToSend)
        );

    } catch (error) {

        console.error(
            "Telegram sendData error:",
            error
        );

    }

}


/* =====================================================
   START
   ===================================================== */

showHome();
updateBalance();