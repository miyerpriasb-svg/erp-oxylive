const STORAGE_KEY = "oxyliveErpState";
const SESSION_KEY = "oxyliveErpSession";
const DEFAULT_PASSWORD = "oxylive123";

const statusMap = {
  pending: { label: "PENDIENTE DIAGNÓSTICO", progress: 10, className: "pending" },
  review: { label: "ESPERANDO APROBACIÓN", progress: 30, className: "review" },
  running: { label: "APROBADO - EN EJECUCIÓN", progress: 60, className: "running" },
  done: { label: "FINALIZADO", progress: 100, className: "done" },
  void: { label: "ANULADO", progress: 0, className: "void" }
};

const demoState = () => ({
  nextOrder: 4,
  users: [
    { id: "u1", name: "Laura Méndez", username: "admin", password: DEFAULT_PASSWORD, role: "Administrador" },
    { id: "u2", name: "Carlos Rivas", username: "coordinador", password: DEFAULT_PASSWORD, role: "Coordinador" },
    { id: "u3", name: "Paola Duarte", username: "recepcion", password: DEFAULT_PASSWORD, role: "Recepcionista" },
    { id: "u4", name: "Miguel Torres", username: "campo", password: DEFAULT_PASSWORD, role: "Tecnico Campo" },
    { id: "u5", name: "Andrés Pinto", username: "taller", password: DEFAULT_PASSWORD, role: "Tecnico Taller" }
  ],
  clients: [
    { id: "c1", name: "Clínica Santa Rosa", nit: "900.125.440-1" },
    { id: "c2", name: "HomeCare Respiratorio SAS", nit: "830.442.901-8" },
    { id: "c3", name: "Oxígeno Vital IPS", nit: "901.778.233-4" }
  ],
  inventory: [
    { id: "p1", name: "Filtro HEPA", unit: "unidad", min: 5, qty: 7 },
    { id: "p2", name: "Kit tamiz molecular", unit: "kit", min: 4, qty: 3 },
    { id: "p3", name: "Válvula check", unit: "unidad", min: 6, qty: 12 },
    { id: "p4", name: "Manguera de oxígeno", unit: "metro", min: 10, qty: 18 }
  ],
  kardex: [
    { id: "k1", date: today(), partId: "p2", type: "entrada", qty: 3, reason: "Inventario inicial" },
    { id: "k2", date: today(), partId: "p1", type: "entrada", qty: 7, reason: "Inventario inicial" }
  ],
  orders: [
    {
      id: "ODS-001",
      clientId: "c1",
      type: "concentrador-portatil",
      route: "campo",
      techId: "u4",
      status: "review",
      reception: {
        serial: "INV-P5-2408",
        physical: "Carcasa con desgaste leve",
        power: "Enciende",
        accessories: "Cargador: CH-8841, batería: BAT-1902"
      },
      notes: "Cliente reporta baja pureza de oxígeno.",
      report: "Válvulas con respuesta lenta, filtros saturados. Requiere autorización para cambio.",
      closeNotes: "",
      partsUsed: []
    },
    {
      id: "ODS-002",
      clientId: "c2",
      type: "lote-tamices",
      route: "taller",
      techId: "u5",
      status: "running",
      reception: {
        batch: [
          { brand: "Devilbiss", model: "525KS", qty: 4 },
          { brand: "Invacare", model: "Perfecto2", qty: 2 }
        ]
      },
      notes: "Lote para regeneración y prueba de pureza.",
      report: "Fast-track aprobado por taller. Tamices en proceso.",
      closeNotes: "",
      partsUsed: []
    },
    {
      id: "ODS-003",
      clientId: "c3",
      type: "concentrador-estacionario",
      route: "campo",
      techId: "u4",
      status: "pending",
      reception: {
        serial: "ST-90881",
        physical: "Completo, sin golpes",
        power: "No enciende",
        accessories: ""
      },
      notes: "Equipo estacionario pendiente de diagnóstico.",
      report: "",
      closeNotes: "",
      partsUsed: []
    }
  ]
});

function today() {
  return new Date().toISOString().slice(0, 10);
}

function uid(prefix) {
  return `${prefix}${Date.now().toString(36)}${Math.random().toString(36).slice(2, 6)}`;
}

function getState() {
  const saved = localStorage.getItem(STORAGE_KEY);
  if (!saved) {
    const state = demoState();
    saveState(state);
    return state;
  }
  try {
    return JSON.parse(saved);
  } catch {
    const state = demoState();
    saveState(state);
    return state;
  }
}

function saveState(state) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
}

function getSession() {
  const raw = localStorage.getItem(SESSION_KEY);
  return raw ? JSON.parse(raw) : null;
}

function setSession(user) {
  localStorage.setItem(SESSION_KEY, JSON.stringify({ id: user.id, name: user.name, role: user.role }));
}

function clearSession() {
  localStorage.removeItem(SESSION_KEY);
}

function isTech(role) {
  return role === "Tecnico Campo" || role === "Tecnico Taller";
}

function canSeeRole(element, role) {
  const roles = element.dataset.roles;
  return !roles || roles.split(",").map((item) => item.trim()).includes(role);
}

function requireSession(expectedPage) {
  const session = getSession();
  if (!session) {
    window.location.href = "login.html";
    return null;
  }
  if (expectedPage === "admin" && isTech(session.role)) {
    window.location.href = "index.html";
    return null;
  }
  if (expectedPage === "tech" && !isTech(session.role)) {
    window.location.href = "admin.html";
    return null;
  }
  return session;
}

function clientName(state, id) {
  return state.clients.find((client) => client.id === id)?.name || "Cliente no registrado";
}

function userName(state, id) {
  return state.users.find((user) => user.id === id)?.name || "Sin asignar";
}

function partName(state, id) {
  return state.inventory.find((part) => part.id === id)?.name || "Repuesto eliminado";
}

function typeLabel(type) {
  return {
    "concentrador-estacionario": "Concentrador estacionario",
    "concentrador-portatil": "Concentrador portátil",
    "lote-tamices": "Lote de tamices"
  }[type] || type;
}

function routeLabel(route) {
  return route === "taller" ? "Taller fast-track" : "Campo con aprobación";
}

function statusPill(status) {
  const meta = statusMap[status] || statusMap.pending;
  return `<span class="pill ${meta.className}">${meta.label}</span>`;
}

function progressBar(status) {
  const meta = statusMap[status] || statusMap.pending;
  return `<div class="progress-track" aria-label="Avance ${meta.progress}%"><span style="width: ${meta.progress}%"></span></div>`;
}

function empty(message) {
  return `<div class="empty-state">${message}</div>`;
}

function initLogin() {
  getState();
  document.querySelectorAll("[data-fill-user]").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelector("#username").value = button.dataset.fillUser;
      document.querySelector("#password").value = DEFAULT_PASSWORD;
    });
  });

  document.querySelector("#loginForm").addEventListener("submit", (event) => {
    event.preventDefault();
    const state = getState();
    const username = document.querySelector("#username").value.trim().toLowerCase();
    const password = document.querySelector("#password").value;
    const user = state.users.find((item) => item.username.toLowerCase() === username && item.password === password);
    const error = document.querySelector("#loginError");
    if (!user) {
      error.textContent = "Usuario o contraseña incorrectos.";
      error.hidden = false;
      return;
    }
    setSession(user);
    window.location.href = isTech(user.role) ? "index.html" : "admin.html";
  });
}

function initShell(session) {
  const label = document.querySelector("#sessionName");
  if (label) label.textContent = `${session.name} · ${session.role}`;
  const logout = document.querySelector("#logoutBtn");
  if (logout) {
    logout.addEventListener("click", () => {
      clearSession();
      window.location.href = "login.html";
    });
  }
}

function initTabs(session) {
  document.querySelectorAll("[data-roles]").forEach((element) => {
    if (!canSeeRole(element, session.role)) element.hidden = true;
  });

  document.querySelectorAll(".tab-button").forEach((button) => {
    button.addEventListener("click", () => {
      document.querySelectorAll(".tab-button").forEach((item) => item.classList.remove("is-active"));
      document.querySelectorAll(".tab-panel").forEach((item) => item.classList.remove("is-active"));
      button.classList.add("is-active");
      document.querySelector(`#${button.dataset.tab}`).classList.add("is-active");
    });
  });
}

function renderAdmin() {
  renderDashboard();
  renderOrderFormOptions();
  renderEquipmentFields();
  renderAdminOrders();
  renderInventory();
  renderDirectory();
}

function renderDashboard() {
  const state = getState();
  const counts = {
    pending: state.orders.filter((order) => order.status === "pending").length,
    review: state.orders.filter((order) => order.status === "review").length,
    running: state.orders.filter((order) => order.status === "running").length,
    done: state.orders.filter((order) => order.status === "done").length
  };
  const critical = state.inventory.filter((part) => part.qty <= part.min).length;
  document.querySelector("#dashboardCards").innerHTML = [
    ["Pendientes", counts.pending],
    ["En aprobación", counts.review],
    ["En ejecución", counts.running],
    ["Stock crítico", critical]
  ].map(([label, value]) => `<article class="summary-card"><strong>${value}</strong><span>${label}</span></article>`).join("");

  const alerts = state.inventory.filter((part) => part.qty <= part.min);
  document.querySelector("#stockAlerts").innerHTML = alerts.length
    ? alerts.map((part) => `<div class="list-row stock-critical"><strong>${part.name}</strong><span>${part.qty} ${part.unit} · mínimo ${part.min}</span></div>`).join("")
    : empty("No hay repuestos en nivel crítico.");
}

function renderOrderFormOptions() {
  const state = getState();
  const clientSelect = document.querySelector("#odsClient");
  const techSelect = document.querySelector("#odsTech");
  if (!clientSelect || !techSelect) return;
  clientSelect.innerHTML = state.clients.map((client) => `<option value="${client.id}">${client.name} · ${client.nit}</option>`).join("");
  techSelect.innerHTML = state.users
    .filter((user) => isTech(user.role))
    .map((user) => `<option value="${user.id}">${user.name} · ${user.role.replace("Tecnico ", "")}</option>`)
    .join("");
}

function renderEquipmentFields() {
  const host = document.querySelector("#equipmentFields");
  const type = document.querySelector("#odsType")?.value;
  if (!host) return;

  if (type === "lote-tamices") {
    host.innerHTML = `
      <div class="stack">
        <div id="tamizRows">
          <div class="tamiz-row">
            <label>Marca<input data-tamiz="brand" required></label>
            <label>Modelo<input data-tamiz="model" required></label>
            <label>Cantidad<input data-tamiz="qty" type="number" min="1" required></label>
            <button class="icon-button" type="button" data-remove-tamiz title="Eliminar línea">×</button>
          </div>
        </div>
        <button id="addTamizRow" class="secondary-action" type="button">Agregar línea</button>
      </div>
    `;
    document.querySelector("#addTamizRow").addEventListener("click", addTamizRow);
    host.querySelector("[data-remove-tamiz]").addEventListener("click", removeTamizRow);
    return;
  }

  const accessoryField = type === "concentrador-portatil"
    ? `<label>Accesorios y seriales<textarea id="equipmentAccessories" rows="2" required placeholder="Cargador, batería, bolso y seriales"></textarea></label>`
    : "";

  host.innerHTML = `
    <div class="form-grid">
      <label>Serial del equipo<input id="equipmentSerial" required></label>
      <label>Encendido
        <select id="equipmentPower" required>
          <option>Enciende</option>
          <option>No enciende</option>
          <option>Intermitente</option>
        </select>
      </label>
    </div>
    <label>Estado físico<textarea id="equipmentPhysical" rows="2" required placeholder="Carcasa, pantalla, ruedas, golpes, faltantes"></textarea></label>
    ${accessoryField}
  `;
}

function addTamizRow() {
  const row = document.createElement("div");
  row.className = "tamiz-row";
  row.innerHTML = `
    <label>Marca<input data-tamiz="brand" required></label>
    <label>Modelo<input data-tamiz="model" required></label>
    <label>Cantidad<input data-tamiz="qty" type="number" min="1" required></label>
    <button class="icon-button" type="button" data-remove-tamiz title="Eliminar línea">×</button>
  `;
  row.querySelector("[data-remove-tamiz]").addEventListener("click", removeTamizRow);
  document.querySelector("#tamizRows").appendChild(row);
}

function removeTamizRow(event) {
  const rows = document.querySelectorAll(".tamiz-row");
  if (rows.length > 1) event.currentTarget.closest(".tamiz-row").remove();
}

function captureReception(type) {
  if (type === "lote-tamices") {
    const batch = [...document.querySelectorAll(".tamiz-row")].map((row) => ({
      brand: row.querySelector('[data-tamiz="brand"]').value.trim(),
      model: row.querySelector('[data-tamiz="model"]').value.trim(),
      qty: Number(row.querySelector('[data-tamiz="qty"]').value)
    }));
    return { batch };
  }
  return {
    serial: document.querySelector("#equipmentSerial").value.trim(),
    physical: document.querySelector("#equipmentPhysical").value.trim(),
    power: document.querySelector("#equipmentPower").value,
    accessories: document.querySelector("#equipmentAccessories")?.value.trim() || ""
  };
}

function createOrder(event) {
  event.preventDefault();
  const state = getState();
  const type = document.querySelector("#odsType").value;
  const order = {
    id: `ODS-${String(state.nextOrder).padStart(3, "0")}`,
    clientId: document.querySelector("#odsClient").value,
    type,
    route: document.querySelector("#odsRoute").value,
    techId: document.querySelector("#odsTech").value,
    status: "pending",
    reception: captureReception(type),
    notes: document.querySelector("#odsNotes").value.trim(),
    report: "",
    closeNotes: "",
    partsUsed: []
  };
  state.nextOrder += 1;
  state.orders.unshift(order);
  saveState(state);
  event.currentTarget.reset();
  renderAdmin();
}

function renderAdminOrders() {
  const state = getState();
  const session = getSession();
  const host = document.querySelector("#adminOrders");
  if (!host) return;
  host.innerHTML = state.orders.length
    ? state.orders.map((order) => orderCard(state, order, session, "admin")).join("")
    : empty("Aún no hay órdenes de servicio.");

  host.querySelectorAll("[data-approve]").forEach((button) => button.addEventListener("click", approveOrder));
  host.querySelectorAll("[data-void]").forEach((button) => button.addEventListener("click", voidOrder));
}

function orderCard(state, order, session, mode) {
  const canApprove = mode === "admin" && order.status === "review" && session.role !== "Recepcionista";
  const canVoid = mode === "admin" && order.status !== "done" && order.status !== "void" && session.role !== "Recepcionista";
  const report = order.report ? `<p class="microcopy"><strong>Reporte:</strong> ${escapeHtml(order.report)}</p>` : "";
  const close = order.closeNotes ? `<p class="microcopy"><strong>Cierre:</strong> ${escapeHtml(order.closeNotes)}</p>` : "";
  return `
    <article class="order-card">
      <div class="order-head">
        <div>
          <strong>${order.id} · ${clientName(state, order.clientId)}</strong>
          <div class="order-meta">${typeLabel(order.type)} · ${routeLabel(order.route)} · ${userName(state, order.techId)}</div>
        </div>
        ${statusPill(order.status)}
      </div>
      ${progressBar(order.status)}
      <p class="microcopy">${escapeHtml(order.notes || "Sin observaciones de recepción.")}</p>
      ${renderReception(order)}
      ${report}
      ${close}
      <div class="action-row">
        ${canApprove ? `<button class="success-action" type="button" data-approve="${order.id}">Autorizar ejecución</button>` : ""}
        ${canVoid ? `<button class="danger-action" type="button" data-void="${order.id}">Anular ODS</button>` : ""}
      </div>
    </article>
  `;
}

function renderReception(order) {
  if (order.type === "lote-tamices") {
    const rows = order.reception.batch?.map((item) => `${escapeHtml(item.brand)} ${escapeHtml(item.model)} (${item.qty})`).join(", ");
    return `<p class="microcopy"><strong>Lote:</strong> ${rows || "Sin líneas registradas"}</p>`;
  }
  return `<p class="microcopy"><strong>Recepción:</strong> serial ${escapeHtml(order.reception.serial)}, ${escapeHtml(order.reception.power)}, ${escapeHtml(order.reception.physical)}${order.reception.accessories ? ` · ${escapeHtml(order.reception.accessories)}` : ""}</p>`;
}

function approveOrder(event) {
  const state = getState();
  const order = state.orders.find((item) => item.id === event.currentTarget.dataset.approve);
  if (order) {
    order.status = "running";
    order.report = `${order.report}\nAutorizado por coordinación para iniciar ejecución.`.trim();
    saveState(state);
    renderAdmin();
  }
}

function voidOrder(event) {
  const state = getState();
  const order = state.orders.find((item) => item.id === event.currentTarget.dataset.void);
  if (order) {
    order.status = "void";
    saveState(state);
    renderAdmin();
  }
}

function renderInventory() {
  const state = getState();
  const table = document.querySelector("#inventoryTable");
  const movementPart = document.querySelector("#movementPart");
  if (!table || !movementPart) return;

  table.innerHTML = `
    <div class="table-row"><span>Repuesto</span><span>Stock</span><span>Mínimo</span><span>Estado</span></div>
    ${state.inventory.map((part) => `
      <div class="table-row ${part.qty <= part.min ? "stock-critical" : ""}">
        <strong>${part.name}</strong>
        <span>${part.qty} ${part.unit}</span>
        <span>${part.min}</span>
        <span>${part.qty <= part.min ? "CRÍTICO" : "OK"}</span>
      </div>
    `).join("")}
  `;
  movementPart.innerHTML = state.inventory.map((part) => `<option value="${part.id}">${part.name}</option>`).join("");

  const kardex = [...state.kardex].reverse().slice(0, 12);
  document.querySelector("#kardexList").innerHTML = kardex.length
    ? kardex.map((entry) => `<div class="list-row"><strong>${entry.date} · ${partName(state, entry.partId)}</strong><span>${entry.type.toUpperCase()} ${entry.qty} · ${escapeHtml(entry.reason)}</span></div>`).join("")
    : empty("Sin movimientos de kardex.");
}

function createPart(event) {
  event.preventDefault();
  const state = getState();
  const part = {
    id: uid("p"),
    name: document.querySelector("#partName").value.trim(),
    unit: document.querySelector("#partUnit").value.trim(),
    min: Number(document.querySelector("#partMin").value),
    qty: Number(document.querySelector("#partQty").value)
  };
  state.inventory.push(part);
  state.kardex.push({ id: uid("k"), date: today(), partId: part.id, type: "entrada", qty: part.qty, reason: "Alta de catálogo" });
  saveState(state);
  event.currentTarget.reset();
  renderAdmin();
}

function createMovement(event) {
  event.preventDefault();
  const state = getState();
  const partId = document.querySelector("#movementPart").value;
  const type = document.querySelector("#movementType").value;
  const qty = Number(document.querySelector("#movementQty").value);
  const part = state.inventory.find((item) => item.id === partId);
  if (!part) return;
  part.qty += type === "entrada" ? qty : -qty;
  if (part.qty < 0) part.qty = 0;
  state.kardex.push({ id: uid("k"), date: today(), partId, type, qty, reason: document.querySelector("#movementReason").value.trim() });
  saveState(state);
  event.currentTarget.reset();
  renderAdmin();
}

function renderDirectory() {
  const state = getState();
  const clients = document.querySelector("#clientList");
  const users = document.querySelector("#userList");
  if (clients) {
    clients.innerHTML = state.clients.map((client) => `<div class="list-row"><strong>${client.name}</strong><span>${client.nit}</span></div>`).join("");
  }
  if (users) {
    users.innerHTML = state.users.map((user) => `<div class="list-row"><strong>${user.name}</strong><span>${user.role} · ${user.username}</span></div>`).join("");
  }
}

function createClient(event) {
  event.preventDefault();
  const state = getState();
  state.clients.push({
    id: uid("c"),
    name: document.querySelector("#clientName").value.trim(),
    nit: document.querySelector("#clientNit").value.trim()
  });
  saveState(state);
  event.currentTarget.reset();
  renderAdmin();
}

function createUser(event) {
  event.preventDefault();
  const state = getState();
  state.users.push({
    id: uid("u"),
    name: document.querySelector("#userName").value.trim(),
    username: document.querySelector("#userLogin").value.trim(),
    password: DEFAULT_PASSWORD,
    role: document.querySelector("#userRole").value
  });
  saveState(state);
  event.currentTarget.reset();
  renderAdmin();
}

function initAdmin() {
  const session = requireSession("admin");
  if (!session) return;
  initShell(session);
  initTabs(session);
  renderAdmin();

  document.querySelector("#odsType").addEventListener("change", renderEquipmentFields);
  document.querySelector("#odsForm").addEventListener("submit", createOrder);
  document.querySelector("#partForm")?.addEventListener("submit", createPart);
  document.querySelector("#manualMovementForm")?.addEventListener("submit", createMovement);
  document.querySelector("#clientForm")?.addEventListener("submit", createClient);
  document.querySelector("#userForm")?.addEventListener("submit", createUser);
  document.querySelector("#resetDemoBtn").addEventListener("click", () => {
    saveState(demoState());
    renderAdmin();
  });
}

function initTech() {
  const session = requireSession("tech");
  if (!session) return;
  initShell(session);
  renderTech(session);
  document.querySelector("#techReportForm").addEventListener("submit", submitTechReport);
  document.querySelector("#closeOrderForm").addEventListener("submit", closeOrder);
  document.querySelector("#closeOrder").addEventListener("change", renderPartsUsed);
}

function assignedOrders(state, session) {
  return state.orders.filter((order) => order.techId === session.id && order.status !== "void");
}

function renderTech(session) {
  const state = getState();
  const orders = assignedOrders(state, session);
  const active = orders.filter((order) => order.status !== "done");
  document.querySelector("#techOrders").innerHTML = orders.length
    ? orders.map((order) => orderCard(state, order, session, "tech")).join("")
    : empty("No tienes órdenes asignadas.");

  const reportable = active.filter((order) => order.status === "pending");
  document.querySelector("#reportOrder").innerHTML = reportable.length
    ? reportable.map((order) => `<option value="${order.id}">${order.id} · ${clientName(state, order.clientId)}</option>`).join("")
    : `<option value="">Sin ODS pendientes de diagnóstico</option>`;
  document.querySelector("#techReportForm button").disabled = reportable.length === 0;

  const closable = active.filter((order) => order.status === "running");
  document.querySelector("#closeOrder").innerHTML = closable.length
    ? closable.map((order) => `<option value="${order.id}">${order.id} · ${clientName(state, order.clientId)}</option>`).join("")
    : `<option value="">Sin ODS en ejecución</option>`;
  document.querySelector("#closeOrderForm button").disabled = closable.length === 0;
  renderPartsUsed();
}

function submitTechReport(event) {
  event.preventDefault();
  const state = getState();
  const id = document.querySelector("#reportOrder").value;
  const order = state.orders.find((item) => item.id === id);
  if (!order) return;
  const report = [
    `Válvulas: ${document.querySelector("#checkValves").value}`,
    `Compresor: ${document.querySelector("#checkCompressor").value}`,
    `Filtros: ${document.querySelector("#checkFilters").value}`,
    document.querySelector("#techReport").value.trim()
  ].join(". ");
  order.report = report;
  order.status = order.route === "taller" ? "running" : "review";
  saveState(state);
  event.currentTarget.reset();
  renderTech(getSession());
}

function renderPartsUsed() {
  const state = getState();
  const host = document.querySelector("#partsUsed");
  if (!host) return;
  host.innerHTML = state.inventory.length
    ? state.inventory.map((part) => `
      <div class="parts-row">
        <label>${part.name} <span class="microcopy">Disponible: ${part.qty} ${part.unit}</span></label>
        <input data-part-used="${part.id}" type="number" min="0" max="${part.qty}" value="0">
      </div>
    `).join("")
    : empty("No hay repuestos en catálogo.");
}

function closeOrder(event) {
  event.preventDefault();
  const state = getState();
  const id = document.querySelector("#closeOrder").value;
  const order = state.orders.find((item) => item.id === id);
  if (!order) return;

  const used = [...document.querySelectorAll("[data-part-used]")]
    .map((input) => ({ partId: input.dataset.partUsed, qty: Number(input.value) }))
    .filter((item) => item.qty > 0);

  used.forEach((item) => {
    const part = state.inventory.find((candidate) => candidate.id === item.partId);
    if (!part) return;
    const qty = Math.min(part.qty, item.qty);
    part.qty -= qty;
    state.kardex.push({ id: uid("k"), date: today(), partId: item.partId, type: "salida", qty, reason: `Cierre ${order.id}` });
    item.qty = qty;
  });

  order.partsUsed = used;
  order.closeNotes = document.querySelector("#closeNotes").value.trim();
  order.status = "done";
  saveState(state);
  event.currentTarget.reset();
  renderTech(getSession());
}

function escapeHtml(value) {
  return String(value || "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.addEventListener("DOMContentLoaded", () => {
  if (document.querySelector("#loginForm")) initLogin();
  if (document.body.dataset.page === "admin") initAdmin();
  if (document.body.dataset.page === "tech") initTech();
});
