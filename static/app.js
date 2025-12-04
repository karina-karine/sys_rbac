// Глобальні змінні
let currentUser = null
let authToken = null

let currentSortColumn = null
let currentSortDirection = "asc"
let allPatients = []
let allAppointments = []
let allMedicalRecords = []
let allUsers = []
let allDepartments = []

// Import Bootstrap
const bootstrap = window.bootstrap

// API функції
const API_BASE = "/api"

async function apiRequest(endpoint, options = {}) {
  const headers = {
    "Content-Type": "application/json",
    ...options.headers,
  }

  if (authToken) {
    headers["Authorization"] = `Bearer ${authToken}`
  }

  try {
    const response = await fetch(`${API_BASE}${endpoint}`, {
      ...options,
      headers,
    })

    if (response.status === 401) {
      console.log("[v0] Помилка авторизації 401, виконую logout")
      logout()
      throw new Error("Сесія закінчилась. Будь ласка, увійдіть знову.")
    }

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      const errorMessage = errorData.detail || `Помилка сервера: ${response.status}`
      console.error("[v0] API помилка:", errorMessage)
      throw new Error(errorMessage)
    }

    // Handle cases where response might be empty (e.g., DELETE requests)
    if (response.status === 204) {
      return null
    }

    return await response.json()
  } catch (error) {
    console.error("[v0] API request failed:", error)
    throw error
  }
}

// Авторизація
document.getElementById("loginForm")?.addEventListener("submit", async (e) => {
  e.preventDefault()

  const username = document.getElementById("username").value
  const password = document.getElementById("password").value

  console.log("[v0] Спроба входу для користувача:", username)

  try {
    const data = await apiRequest("/auth/login", {
      method: "POST",
      body: JSON.stringify({ username, password }),
    })

    console.log("[v0] Відповідь сервера:", data)

    if (!data || !data.access_token) {
      throw new Error("Сервер не повернув токен авторизації. Перевірте правильність даних.")
    }

    authToken = data.access_token
    localStorage.setItem("authToken", authToken)
    console.log("[v0] Токен збережено успішно")

    await loadCurrentUser()
    showMainApp()
  } catch (error) {
    console.error("[v0] Помилка входу:", error)
    alert("Помилка авторизації: " + error.message)
  }
})

async function loadCurrentUser() {
  try {
    console.log("[v0] Завантаження даних користувача...")
    currentUser = await apiRequest("/auth/me")
    console.log("[v0] Дані користувача завантажено:", currentUser)

    const nameElement = document.getElementById("currentUserName")
    const rolesElement = document.getElementById("currentUserRoles")

    if (nameElement && currentUser.full_name) {
      nameElement.textContent = currentUser.full_name
    }

    if (rolesElement && currentUser.roles) {
      const roles = currentUser.roles.map((r) => r.name).join(", ")
      rolesElement.textContent = roles
    }
  } catch (error) {
    console.error("[v0] Помилка завантаження користувача:", error)
    // Don't alert here, as it might be a session expiry during normal operation
    // alert("Помилка завантаження даних користувача: " + error.message)
  }
}

function logout() {
  console.log("[v0] Вихід з системи")
  authToken = null
  currentUser = null
  localStorage.removeItem("authToken")
  showLoginScreen()
}

function showLoginScreen() {
  const loginScreen = document.getElementById("loginScreen")
  const mainApp = document.getElementById("mainApp")

  if (loginScreen) loginScreen.classList.remove("hidden")
  if (mainApp) mainApp.classList.add("hidden")
}

function showMainApp() {
  const loginScreen = document.getElementById("loginScreen")
  const mainApp = document.getElementById("mainApp")

  if (loginScreen) loginScreen.classList.add("hidden")
  if (mainApp) mainApp.classList.remove("hidden")

  // Default to dashboard on login
  loadDashboard()
  document.querySelector(".nav-item[data-page='dashboard']").classList.add("active")
}

window.addEventListener("DOMContentLoaded", () => {
  const savedToken = localStorage.getItem("authToken")

  if (savedToken) {
    console.log("[v0] Знайдено збережений токен, спроба автоматичного входу")
    authToken = savedToken

    loadCurrentUser()
      .then(() => {
        showMainApp()
      })
      .catch((error) => {
        console.error("[v0] Автоматичний вхід не вдався:", error)
        logout()
      })
  } else {
    console.log("[v0] Токен не знайдено, показую екран входу")
    showLoginScreen()
  }
})

// Навігація
document.querySelectorAll(".nav-item[data-page]").forEach((item) => {
  item.addEventListener("click", () => {
    const page = item.getAttribute("data-page")

    document.querySelectorAll(".nav-item").forEach((i) => i.classList.remove("active"))
    item.classList.add("active")

    loadPage(page)
  })
})

function loadPage(page) {
  console.log("[v0] Завантаження сторінки:", page)

  switch (page) {
    case "dashboard":
      loadDashboard()
      break
    case "patients":
      loadPatientsPage() //
      break
    case "appointments":
      loadAppointmentsPage() //
      break
    case "medical-records":
      loadMedicalRecordsPage() //
      break
    case "users":
      loadUsersPage() //
      break
    case "departments":
      loadDepartmentsPage() //
      break
    case "rbac":
      loadRBAC()
      break
    default:
      console.error("[v0] Невідома сторінка:", page)
  }
}

// Панель керування
async function loadDashboard() {
  const content = `
        <h1 class="mb-4"><i class="bi bi-speedometer2"></i> Панель керування</h1>
        
        <div class="row">
            <div class="col-md-3">
                <div class="stat-card" style="--bg-start: #667eea; --bg-end: #764ba2;">
                    <i class="bi bi-people" style="font-size: 2rem;"></i>
                    <h3 id="totalPatients">-</h3>
                    <p>Всього пацієнтів</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="--bg-start: #f093fb; --bg-end: #f5576c;">
                    <i class="bi bi-calendar-check" style="font-size: 2rem;"></i>
                    <h3 id="totalAppointments">-</h3>
                    <p>Записів на сьогодні</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="--bg-start: #4facfe; --bg-end: #00f2fe;">
                    <i class="bi bi-file-medical" style="font-size: 2rem;"></i>
                    <h3 id="totalRecords">-</h3>
                    <p>Медичних записів</p>
                </div>
            </div>
            <div class="col-md-3">
                <div class="stat-card" style="--bg-start: #43e97b; --bg-end: #38f9d7;">
                    <i class="bi bi-person-badge" style="font-size: 2rem;"></i>
                    <h3 id="totalUsers">-</h3>
                    <p>Користувачів системи</p>
                </div>
            </div>
        </div>
        
        <div class="row mt-4">
            <div class="col-md-8">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Останні записи на прийом</h5>
                        <div id="recentAppointments"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-4">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Мої дозволи</h5>
                        <div id="userPermissions"></div>
                    </div>
                </div>
            </div>
        </div>
    `

  document.getElementById("contentArea").innerHTML = content

  // Завантаження статистики
  try {
    const [patients, appointments, records, users] = await Promise.all([
      apiRequest("/patients"),
      apiRequest("/appointments"),
      apiRequest("/medical-records"),
      apiRequest("/users"),
    ])

    document.getElementById("totalPatients").textContent = patients.length
    document.getElementById("totalAppointments").textContent = appointments.filter((a) => {
      return a.appointment_date === new Date().toISOString().split("T")[0]
    }).length
    document.getElementById("totalRecords").textContent = records.length
    document.getElementById("totalUsers").textContent = users.length

    // Останні записи
    const recentHtml = appointments
      .slice(0, 5)
      .map(
        (a) => `
            <div class="d-flex justify-content-between align-items-center mb-2 p-2 border-bottom">
                <div>
                    <strong>Пацієнт ID: ${a.patient_id}</strong><br>
                    <small class="text-muted">${a.appointment_date} ${a.appointment_time}</small>
                </div>
                <span class="badge bg-${getStatusColor(a.status)}">${a.status}</span>
            </div>
        `,
      )
      .join("")
    document.getElementById("recentAppointments").innerHTML = recentHtml || '<p class="text-muted">Немає записів</p>'

    // Дозволи користувача
    const permissions = await apiRequest("/rbac/my-permissions")
    const permHtml = permissions
      .map(
        (p) => `
            <span class="badge bg-primary me-1 mb-1">${p.description}</span>
        `,
      )
      .join("")
    document.getElementById("userPermissions").innerHTML = permHtml
  } catch (error) {
    console.error("Помилка завантаження статистики:", error)
  }
}

// Пацієнти
async function loadPatientsPage() {
  const content = `
        <h2 class="mb-4">Управління пацієнтами</h2>
        
        <div class="mb-3 d-flex justify-content-between align-items-center">
            <input type="text" class="form-control" id="searchPatients" placeholder="Пошук пацієнтів..." style="max-width: 400px;">
            <button class="btn btn-gradient" onclick="showAddPatientModal()">
                <i class="bi bi-plus-circle"></i> Додати пацієнта
            </button>
        </div>
        
        <div class="card">
            <div class="card-body">
                <div id="patientsTable"></div>
            </div>
        </div>
    `

  document.getElementById("contentArea").innerHTML = content

  try {
    allPatients = await apiRequest("/patients")
    displayPatientsTable(allPatients)

    document.getElementById("searchPatients").addEventListener("input", (e) => {
      const search = e.target.value.toLowerCase()
      const filtered = allPatients.filter(
        (p) =>
          p.first_name.toLowerCase().includes(search) ||
          p.last_name.toLowerCase().includes(search) ||
          p.phone.includes(search) ||
          (p.email && p.email.toLowerCase().includes(search)),
      )
      displayPatientsTable(filtered)
    })
  } catch (error) {
    alert("Помилка завантаження пацієнтів: " + error.message)
  }
}

function displayPatientsTable(patients) {
  const html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th onclick="sortTable(allPatients, 'id', displayPatientsTable)" style="cursor: pointer;">
                            ID <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th onclick="sortTable(allPatients, 'last_name', displayPatientsTable)" style="cursor: pointer;">
                            ПІБ <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th onclick="sortTable(allPatients, 'birth_date', displayPatientsTable)" style="cursor: pointer;">
                            Дата народження <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th>Телефон</th>
                        <th>Email</th>
                        <th>Група крові</th>
                        <th>Дії</th>
                    </tr>
                </thead>
                <tbody>
                    ${patients
      .map(
        (p) => `
                        <tr>
                            <td>${p.id}</td>
                            <td>${p.last_name} ${p.first_name} ${p.middle_name || ""}</td>
                            <td>${p.birth_date}</td>
                            <td>${p.phone}</td>
                            <td>${p.email || "-"}</td>
                            <td><span class="badge bg-danger">${p.blood_type || "—"}</span></td>
                            <td class="table-actions">
                                <button class="btn btn-sm btn-warning" onclick="editPatient(${p.id})">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deletePatient(${p.id})">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `,
      )
      .join("")}
                </tbody>
            </table>
        </div>
    `

  document.getElementById("patientsTable").innerHTML = html
}

// Записи на прийом
async function loadAppointmentsPage() {
  const content = `
        <h2 class="mb-4">Записи на прийом</h2>
        
        <div class="mb-3 d-flex justify-content-between">
            <button class="btn btn-gradient" onclick="showAddAppointmentModal()">
                <i class="bi bi-plus-circle"></i> Новий запис
            </button>
        </div>
        
        <div class="card">
            <div class="card-body">
                <div class="row mb-3">
                    <div class="col-md-3">
                        <label class="form-label">Фільтр за датою</label>
                        <input type="date" class="form-control" id="filterDate">
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">Статус</label>
                        <select class="form-select" id="filterStatus">
                            <option value="">Всі статуси</option>
                            <option value="scheduled">Заплановано</option>
                            <option value="confirmed">Підтверджено</option>
                            <option value="completed">Завершено</option>
                            <option value="cancelled">Скасовано</option>
                        </select>
                    </div>
                    <div class="col-md-3">
                        <label class="form-label">&nbsp;</label>
                        <button class="btn btn-primary d-block" onclick="applyAppointmentFilters()">
                            <i class="bi bi-funnel"></i> Застосувати
                        </button>
                    </div>
                </div>
                <div id="appointmentsTable"></div>
            </div>
        </div>
    `

  document.getElementById("contentArea").innerHTML = content

  try {
    allAppointments = await apiRequest("/appointments")
    displayAppointmentsTable(allAppointments)
  } catch (error) {
    alert("Помилка завантаження записів: " + error.message)
  }
}

function applyAppointmentFilters() {
  const dateFilter = document.getElementById("filterDate").value
  const statusFilter = document.getElementById("filterStatus").value

  let filtered = [...allAppointments]

  if (dateFilter) {
    filtered = filtered.filter((a) => a.appointment_date === dateFilter)
  }

  if (statusFilter) {
    filtered = filtered.filter((a) => a.status === statusFilter)
  }

  displayAppointmentsTable(filtered)
}

function displayAppointmentsTable(appointments) {
  const statusColors = {
    scheduled: "warning",
    confirmed: "info",
    completed: "success",
    cancelled: "danger",
  }

  const statusLabels = {
    scheduled: "Заплановано",
    confirmed: "Підтверджено",
    completed: "Завершено",
    cancelled: "Скасовано",
  }

  const html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th onclick="sortTable(allAppointments, 'id', displayAppointmentsTable)" style="cursor: pointer;">
                            ID <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th onclick="sortTable(allAppointments, 'appointment_date', displayAppointmentsTable)" style="cursor: pointer;">
                            Дата <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th>Час</th>
                        <th>Пацієнт</th>
                        <th>Лікар</th>
                        <th onclick="sortTable(allAppointments, 'status', displayAppointmentsTable)" style="cursor: pointer;">
                            Статус <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th>Причина</th>
                        <th>Дії</th>
                    </tr>
                </thead>
                <tbody>
                    ${appointments
      .map(
        (a) => `
                        <tr>
                            <td>${a.id}</td>
                            <td>${a.appointment_date}</td>
                            <td>${a.appointment_time}</td>
                            <td>Пацієнт #${a.patient_id}</td>
                            <td>Лікар #${a.doctor_id}</td>
                            <td><span class="badge bg-${statusColors[a.status] || "secondary"}">${statusLabels[a.status] || a.status}</span></td>
                            <td>${a.reason.substring(0, 50)}${a.reason.length > 50 ? "..." : ""}</td>
                            <td class="table-actions">
                                ${a.status !== "cancelled" && a.status !== "completed"
            ? `
                                    <button class="btn btn-sm btn-success" onclick="completeAppointment(${a.id})">
                                        <i class="bi bi-check-circle"></i>
                                    </button>
                                    <button class="btn btn-sm btn-danger" onclick="cancelAppointment(${a.id})">
                                        <i class="bi bi-x-circle"></i>
                                    </button>
                                `
            : ""
          }
                            </td>
                        </tr>
                    `,
      )
      .join("")}
                </tbody>
            </table>
        </div>
    `
  document.getElementById("appointmentsTable").innerHTML = html
}

// Медичні записи
async function loadMedicalRecordsPage() {
  const content = `
        <h2 class="mb-4">Медичні записи</h2>
        
        <div class="mb-3 d-flex justify-content-between align-items-center">
            <input type="text" class="form-control" id="searchRecords" placeholder="Пошук за діагнозом..." style="max-width: 400px;">
            <button class="btn btn-gradient" onclick="showAddMedicalRecordModal()">
                <i class="bi bi-plus-circle"></i> Новий запис
            </button>
        </div>
        
        <div class="card">
            <div class="card-body">
                <div id="medicalRecordsTable"></div>
            </div>
        </div>
    `

  document.getElementById("contentArea").innerHTML = content

  try {
    allMedicalRecords = await apiRequest("/medical-records")
    displayMedicalRecordsTable(allMedicalRecords)

    document.getElementById("searchRecords").addEventListener("input", (e) => {
      const search = e.target.value.toLowerCase()
      const filtered = allMedicalRecords.filter(
        (r) => r.diagnosis.toLowerCase().includes(search) || r.treatment.toLowerCase().includes(search),
      )
      displayMedicalRecordsTable(filtered)
    })
  } catch (error) {
    alert("Помилка завантаження записів: " + error.message)
  }
}

function displayMedicalRecordsTable(records) {
  const html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th onclick="sortTable(allMedicalRecords, 'id', displayMedicalRecordsTable)" style="cursor: pointer;">
                            ID <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th>Пацієнт</th>
                        <th>Лікар</th>
                        <th onclick="sortTable(allMedicalRecords, 'diagnosis', displayMedicalRecordsTable)" style="cursor: pointer;">
                            Діагноз <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th>Лікування</th>
                        <th onclick="sortTable(allMedicalRecords, 'visit_date', displayMedicalRecordsTable)" style="cursor: pointer;">
                            Дата візиту <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th>Дії</th>
                    </tr>
                </thead>
                <tbody>
                    ${records
      .map(
        (r) => `
                        <tr>
                            <td>${r.id}</td>
                            <td>Пацієнт #${r.patient_id}</td>
                            <td>Лікар #${r.doctor_id}</td>
                            <td><strong>${r.diagnosis}</strong></td>
                            <td>${r.treatment.substring(0, 50)}${r.treatment.length > 50 ? "..." : ""}</td>
                            <td>${new Date(r.visit_date).toLocaleDateString("uk-UA")}</td>
                            <td class="table-actions">
                                <button class="btn btn-sm btn-warning" onclick="editMedicalRecord(${r.id})">
                                    <i class="bi bi-pencil"></i>
                                </button>
                            </td>
                        </tr>
                    `,
      )
      .join("")}
                </tbody>
            </table>
        </div>
    `
  document.getElementById("medicalRecordsTable").innerHTML = html
}

// Користувачі
async function loadUsersPage() {
  const content = `
        <h2 class="mb-4">Користувачі системи</h2>
        
        <div class="mb-3 d-flex justify-content-between">
            <input type="text" class="form-control" id="searchUsers" placeholder="Пошук користувачів..." style="max-width: 400px;">
            <button class="btn btn-gradient" onclick="showAddUserModal()">
                <i class="bi bi-plus-circle"></i> Додати користувача
            </button>
        </div>
        
        <div class="card">
            <div class="card-body">
                <div id="usersTable"></div>
            </div>
        </div>
    `

  document.getElementById("contentArea").innerHTML = content

  try {
    allUsers = await apiRequest("/users")
    displayUsersTable(allUsers)

    document.getElementById("searchUsers").addEventListener("input", (e) => {
      const search = e.target.value.toLowerCase()
      const filtered = allUsers.filter(
        (u) =>
          u.username.toLowerCase().includes(search) ||
          u.full_name.toLowerCase().includes(search) ||
          u.email.toLowerCase().includes(search),
      )
      displayUsersTable(filtered)
    })
  } catch (error) {
    alert("Помилка завантаження користувачів: " + error.message)
  }
}

function displayUsersTable(users) {
  const html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th onclick="sortTable(allUsers, 'id', displayUsersTable)" style="cursor: pointer;">
                            ID <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th onclick="sortTable(allUsers, 'username', displayUsersTable)" style="cursor: pointer;">
                            Username <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th onclick="sortTable(allUsers, 'full_name', displayUsersTable)" style="cursor: pointer;">
                            ПІБ <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th>Email</th>
                        <th>Телефон</th>
                        <th>Ролі</th>
                        <th>Статус</th>
                        <th>Дії</th>
                    </tr>
                </thead>
                <tbody>
                    ${users
      .map(
        (u) => `
                        <tr>
                            <td>${u.id}</td>
                            <td><strong>${u.username}</strong></td>
                            <td>${u.full_name}</td>
                            <td>${u.email}</td>
                            <td>${u.phone || "—"}</td>
                            <td>
                                ${u.roles.map((r) => `<span class="badge bg-primary me-1">${r.name}</span>`).join("")}
                            </td>
                            <td>
                                ${u.is_active
            ? '<span class="badge bg-success">Активний</span>'
            : '<span class="badge bg-danger">Неактивний</span>'
          }
                            </td>
                            <td class="table-actions">
                                <button class="btn btn-sm btn-warning" onclick="editUser(${u.id})">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                ${u.is_active
            ? `<button class="btn btn-sm btn-danger" onclick="toggleUserStatus(${u.id}, false)">
                                        <i class="bi bi-lock"></i>
                                    </button>`
            : `<button class="btn btn-sm btn-success" onclick="toggleUserStatus(${u.id}, true)">
                                        <i class="bi bi-unlock"></i>
                                    </button>`
          }
                            </td>
                        </tr>
                    `,
      )
      .join("")}
                </tbody>
            </table>
        </div>
    `
  document.getElementById("usersTable").innerHTML = html
}

// Відділення
async function loadDepartmentsPage() {
  const content = `
        <h2 class="mb-4">Відділення закладу</h2>
        
        <div class="mb-3 d-flex justify-content-end">
            <button class="btn btn-gradient" onclick="showAddDepartmentModal()">
                <i class="bi bi-plus-circle"></i> Додати відділення
            </button>
        </div>
        
        <div class="card">
            <div class="card-body">
                <div id="departmentsTable"></div>
            </div>
        </div>
    `

  document.getElementById("contentArea").innerHTML = content

  try {
    allDepartments = await apiRequest("/departments")
    displayDepartmentsTable(allDepartments)
  } catch (error) {
    alert("Помилка завантаження відділень: " + error.message)
  }
}

function displayDepartmentsTable(departments) {
  const html = `
        <div class="table-responsive">
            <table class="table table-hover">
                <thead>
                    <tr>
                        <th onclick="sortTable(allDepartments, 'id', displayDepartmentsTable)" style="cursor: pointer;">
                            ID <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th onclick="sortTable(allDepartments, 'name', displayDepartmentsTable)" style="cursor: pointer;">
                            Назва <i class="bi bi-arrow-down-up"></i>
                        </th>
                        <th>Опис</th>
                        <th>Завідувач</th>
                        <th>Телефон</th>
                        <th>Дії</th>
                    </tr>
                </thead>
                <tbody>
                    ${departments
      .map(
        (d) => `
                        <tr>
                            <td>${d.id}</td>
                            <td><strong>${d.name}</strong></td>
                            <td>${d.description || "—"}</td>
                            <td>${d.head_doctor_id ? `Лікар #${d.head_doctor_id}` : "Не призначено"}</td>
                            <td>${d.phone || "—"}</td>
                            <td class="table-actions">
                                <button class="btn btn-sm btn-warning" onclick="editDepartment(${d.id})">
                                    <i class="bi bi-pencil"></i>
                                </button>
                                <button class="btn btn-sm btn-danger" onclick="deleteDepartment(${d.id})">
                                    <i class="bi bi-trash"></i>
                                </button>
                            </td>
                        </tr>
                    `,
      )
      .join("")}
                </tbody>
            </table>
        </div>
    `
  document.getElementById("departmentsTable").innerHTML = html
}

// RBAC - Управління доступом
async function loadRBAC() {
  const content = `
        <h1 class="mb-4"><i class="bi bi-shield-lock"></i> Управління доступом (RBAC)</h1>
        
        <div class="row">
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Ролі в системі</h5>
                        <div id="rolesTable"></div>
                    </div>
                </div>
            </div>
            <div class="col-md-6">
                <div class="card">
                    <div class="card-body">
                        <h5 class="card-title">Дозволи</h5>
                        <div id="permissionsTable"></div>
                    </div>
                </div>
            </div>
        </div>
    `

  document.getElementById("contentArea").innerHTML = content

  try {
    const [roles, permissions] = await Promise.all([apiRequest("/rbac/roles"), apiRequest("/rbac/permissions")])

    displayRolesTable(roles)
    displayPermissionsTable(permissions)
  } catch (error) {
    alert("Помилка завантаження RBAC: " + error.message)
  }
}

function displayRolesTable(roles) {
  const html = `
        <table class="table">
            <thead>
                <tr>
                    <th>Роль</th>
                    <th>Пріоритет</th>
                    <th>Дозволів</th>
                </tr>
            </thead>
            <tbody>
                ${roles
      .map(
        (r) => `
                    <tr>
                        <td><strong>${r.name}</strong><br><small class="text-muted">${r.description}</small></td>
                        <td><span class="badge bg-primary">${r.priority}</span></td>
                        <td><span class="badge bg-info">${r.permissions.length}</span></td>
                    </tr>
                `,
      )
      .join("")}
            </tbody>
        </table>
    `

  document.getElementById("rolesTable").innerHTML = html
}

function displayPermissionsTable(permissions) {
  const grouped = {}
  permissions.forEach((p) => {
    if (!grouped[p.resource]) grouped[p.resource] = []
    grouped[p.resource].push(p)
  })

  const html = Object.entries(grouped)
    .map(
      ([resource, perms]) => `
        <div class="mb-3">
            <h6 class="text-uppercase text-muted">${resource}</h6>
            ${perms
          .map(
            (p) => `
                <span class="badge bg-secondary me-1 mb-1">${p.action}</span>
            `,
          )
          .join("")}
        </div>
    `,
    )
    .join("")

  document.getElementById("permissionsTable").innerHTML = html
}

function sortTable(data, column, displayFunction) {
  if (currentSortColumn === column) {
    currentSortDirection = currentSortDirection === "asc" ? "desc" : "asc"
  } else {
    currentSortColumn = column
    currentSortDirection = "asc"
  }

  // Ensure data is an array before sorting
  if (!Array.isArray(data)) {
    console.error("sortTable: data is not an array", data)
    return
  }

  const sorted = [...data].sort((a, b) => {
    let aVal = a[column]
    let bVal = b[column]

    // Handle null or undefined values for consistent sorting
    if (aVal == null && bVal == null) return 0
    if (aVal == null) return currentSortDirection === "asc" ? -1 : 1
    if (bVal == null) return currentSortDirection === "asc" ? 1 : -1

    if (typeof aVal === "string") {
      aVal = aVal.toLowerCase()
      bVal = bVal.toLowerCase()
    }

    if (currentSortDirection === "asc") {
      return aVal > bVal ? 1 : -1
    } else {
      return aVal < bVal ? 1 : -1
    }
  })

  displayFunction(sorted)
}

// Допоміжні функції
function getStatusColor(status) {
  const colors = {
    scheduled: "primary",
    confirmed: "info",
    in_progress: "warning",
    completed: "success",
    cancelled: "danger",
    no_show: "secondary",
  }
  return colors[status] || "secondary"
}

async function updateAppointmentStatus(id, status) {
  try {
    await apiRequest(`/appointments/${id}`, {
      method: "PUT",
      body: JSON.stringify({ status }),
    })
    loadAppointmentsPage() // Use the updated page loading function
  } catch (error) {
    alert("Помилка оновлення статусу: " + error.message)
  }
}

function showAddPatientModal() {
  const modalElement = document.getElementById("addPatientModal")
  if (!modalElement) {
    console.error("Modal element #addPatientModal not found")
    return
  }
  const modal = new bootstrap.Modal(modalElement)
  document.getElementById("addPatientForm")?.reset()
  modal.show()
}

async function showAddAppointmentModal() {
  const modalElement = document.getElementById("addAppointmentModal")
  if (!modalElement) {
    console.error("Modal element #addAppointmentModal not found")
    return
  }
  const modal = new bootstrap.Modal(modalElement)
  document.getElementById("addAppointmentForm")?.reset()

  try {
    const patients = await apiRequest("/patients")
    const users = await apiRequest("/users")
    const doctors = users.filter((u) => u.roles.some((r) => r.name === "Лікар"))

    const patientSelect = document.getElementById("appointmentPatientSelect")
    if (patientSelect) {
      patientSelect.innerHTML =
        '<option value="">Оберіть пацієнта</option>' +
        patients.map((p) => `<option value="${p.id}">${p.last_name} ${p.first_name} (${p.phone})</option>`).join("")
    }

    const doctorSelect = document.getElementById("appointmentDoctorSelect")
    if (doctorSelect) {
      doctorSelect.innerHTML =
        '<option value="">Оберіть лікаря</option>' +
        doctors.map((d) => `<option value="${d.id}">${d.full_name}</option>`).join("")
    }

    modal.show()
  } catch (error) {
    alert("Помилка завантаження даних: " + error.message)
  }
}

async function showAddMedicalRecordModal() {
  const modalElement = document.getElementById("addMedicalRecordModal")
  if (!modalElement) {
    console.error("Modal element #addMedicalRecordModal not found")
    return
  }
  const modal = new bootstrap.Modal(modalElement)
  document.getElementById("addMedicalRecordForm")?.reset()

  try {
    const patients = await apiRequest("/patients")
    const users = await apiRequest("/users")
    const doctors = users.filter((u) => u.roles.some((r) => r.name === "Лікар"))

    const patientSelect = document.getElementById("medicalRecordPatientSelect")
    if (patientSelect) {
      patientSelect.innerHTML =
        '<option value="">Оберіть пацієнта</option>' +
        patients.map((p) => `<option value="${p.id}">${p.last_name} ${p.first_name}</option>`).join("")
    }

    const doctorSelect = document.getElementById("medicalRecordDoctorSelect")
    if (doctorSelect) {
      doctorSelect.innerHTML =
        '<option value="">Оберіть лікаря</option>' +
        doctors.map((d) => `<option value="${d.id}">${d.full_name}</option>`).join("")
    }

    modal.show()
  } catch (error) {
    alert("Помилка завантаження даних: " + error.message)
  }
}

async function showAddUserModal() {
  const modalElement = document.getElementById("addUserModal")
  if (!modalElement) {
    console.error("Modal element #addUserModal not found")
    return
  }
  const modal = new bootstrap.Modal(modalElement)
  document.getElementById("addUserForm")?.reset()

  try {
    const roles = await apiRequest("/rbac/roles")

    const roleSelect = document.getElementById("userRoleSelect")
    if (roleSelect) {
      roleSelect.innerHTML =
        '<option value="">Оберіть роль</option>' +
        roles.map((r) => `<option value="${r.id}">${r.name}</option>`).join("")
    }

    modal.show()
  } catch (error) {
    alert("Помилка завантаження ролей: " + error.message)
  }
}

async function showAddDepartmentModal() {
  const modalElement = document.getElementById("addDepartmentModal")
  if (!modalElement) {
    console.error("Modal element #addDepartmentModal not found")
    return
  }
  const modal = new bootstrap.Modal(modalElement)
  document.getElementById("addDepartmentForm")?.reset()

  try {
    const users = await apiRequest("/users")
    const doctors = users.filter((u) => u.roles.some((r) => r.name === "Лікар"))

    const headDoctorSelect = document.getElementById("departmentHeadSelect")
    if (headDoctorSelect) {
      headDoctorSelect.innerHTML =
        '<option value="">Не призначено</option>' +
        doctors.map((d) => `<option value="${d.id}">${d.full_name}</option>`).join("")
    }

    modal.show()
  } catch (error) {
    alert("Помилка завантаження лікарів: " + error.message)
  }
}

async function submitAddPatient() {
  const form = document.getElementById("addPatientForm")
  if (!form) return
  const formData = new FormData(form)
  const data = Object.fromEntries(formData.entries())

  try {
    await apiRequest("/patients", { method: "POST", body: JSON.stringify(data) })
    bootstrap.Modal.getInstance(document.getElementById("addPatientModal")).hide()
    alert("Пацієнта успішно додано!")
    loadPatientsPage()
  } catch (error) {
    alert("Помилка додавання пацієнта: " + error.message)
  }
}

async function submitAddAppointment() {
  const form = document.getElementById("addAppointmentForm")
  if (!form) return
  const formData = new FormData(form)
  const data = Object.fromEntries(formData.entries())

  data.patient_id = Number.parseInt(data.patient_id)
  data.doctor_id = Number.parseInt(data.doctor_id)

  try {
    await apiRequest("/appointments", { method: "POST", body: JSON.stringify(data) })
    bootstrap.Modal.getInstance(document.getElementById("addAppointmentModal")).hide()
    alert("Запис на прийом створено!")
    loadAppointmentsPage()
  } catch (error) {
    alert("Помилка створення запису: " + error.message)
  }
}

async function submitAddMedicalRecord() {
  const form = document.getElementById("addMedicalRecordForm")
  if (!form) return
  const formData = new FormData(form)
  const data = Object.fromEntries(formData.entries())

  data.patient_id = Number.parseInt(data.patient_id)
  data.doctor_id = Number.parseInt(data.doctor_id)

  try {
    await apiRequest("/medical-records", { method: "POST", body: JSON.stringify(data) })
    bootstrap.Modal.getInstance(document.getElementById("addMedicalRecordModal")).hide()
    alert("Медичний запис додано!")
    loadMedicalRecordsPage()
  } catch (error) {
    alert("Помилка додавання запису: " + error.message)
  }
}

async function submitAddUser() {
  const form = document.getElementById("addUserForm")
  if (!form) return
  const formData = new FormData(form)
  const data = Object.fromEntries(formData.entries())

  data.role_id = Number.parseInt(data.role_id)

  try {
    const result = await apiRequest("/users", { method: "POST", body: JSON.stringify(data) })
    bootstrap.Modal.getInstance(document.getElementById("addUserModal")).hide()
    alert(`Користувача створено! ID: ${result.id}`)
    loadUsersPage()
  } catch (error) {
    alert("Помилка створення користувача: " + error.message)
  }
}

async function submitAddDepartment() {
  const form = document.getElementById("addDepartmentForm")
  if (!form) return
  const formData = new FormData(form)
  const data = Object.fromEntries(formData.entries())

  if (data.head_doctor_id) {
    data.head_doctor_id = Number.parseInt(data.head_doctor_id)
  } else {
    delete data.head_doctor_id
  }

  try {
    await apiRequest("/departments", { method: "POST", body: JSON.stringify(data) })
    bootstrap.Modal.getInstance(document.getElementById("addDepartmentModal")).hide()
    alert("Відділення створено!")
    loadDepartmentsPage()
  } catch (error) {
    alert("Помилка створення відділення: " + error.message)
  }
}

async function deletePatient(id) {
  if (!confirm("Ви впевнені, що хочете видалити цього пацієнта?")) return

  try {
    await apiRequest(`/patients/${id}`, { method: "DELETE" })
    alert("Пацієнта видалено")
    loadPatientsPage()
  } catch (error) {
    alert("Помилка видалення: " + error.message)
  }
}

async function completeAppointment(id) {
  try {
    await apiRequest(`/appointments/${id}`, {
      method: "PUT",
      body: JSON.stringify({ status: "completed" }),
    })
    alert("Прийом завершено")
    loadAppointmentsPage()
  } catch (error) {
    alert("Помилка: " + error.message)
  }
}

async function cancelAppointment(id) {
  if (!confirm("Скасувати цей запис?")) return

  try {
    await apiRequest(`/appointments/${id}`, {
      method: "PUT",
      body: JSON.stringify({ status: "cancelled" }),
    })
    alert("Запис скасовано")
    loadAppointmentsPage()
  } catch (error) {
    alert("Помилка: " + error.message)
  }
}

async function toggleUserStatus(id, newStatus) {
  try {
    await apiRequest(`/users/${id}`, {
      method: "PUT",
      body: JSON.stringify({ is_active: newStatus }),
    })
    alert(newStatus ? "Користувача активовано" : "Користувача деактивовано")
    loadUsersPage()
  } catch (error) {
    alert("Помилка: " + error.message)
  }
}

async function deleteDepartment(id) {
  if (!confirm("Видалити відділення?")) return

  try {
    await apiRequest(`/departments/${id}`, { method: "DELETE" })
    alert("Відділення видалено")
    loadDepartmentsPage()
  } catch (error) {
    alert("Помилка: " + error.message)
  }
}

function editPatient(id) {
  alert(`Редагування пацієнта ID: ${id}\n(Функція буде реалізована)`)
}

function viewAppointment(id) {
  alert(`Детальний перегляд запису ID: ${id}\n(Функція буде реалізована)`)
}

function viewMedicalRecord(id) {
  alert(`Перегляд медичного запису ID: ${id}\n(Функція буде реалізована)`)
}

function editMedicalRecord(id) {
  alert(`Редагування запису ID: ${id}\n(Функція буде реалізована)`)
}

function viewUser(id) {
  alert(`Перегляд користувача ID: ${id}\n(Функція буде реалізована)`)
}

function editUser(id) {
  alert(`Редагування користувача ID: ${id}\n(Функція буде реалізована)`)
}

function viewDepartment(id) {
  alert(`Перегляд відділення ID: ${id}\n(Функція буде реалізована)`)
}

function editDepartment(id) {
  alert(`Редагування відділення ID: ${id}\n(Функція буде реалізована)`)
}
